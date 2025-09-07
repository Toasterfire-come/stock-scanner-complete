#!/usr/bin/env bash

set -euo pipefail

# curl-based site scanner and fixer helper
#
# Subcommands:
#   scan     - crawl the site, collect page and asset HTTP errors
#   suggest  - read scan output and generate human-readable fix suggestions
#   fix      - optional: apply auto-fixable replacements in a local repo (redirects, http->https)
#
# Examples:
#   ./scan_and_fix.sh scan --base-url https://tradescanpro.com --out-dir /workspace/scan_output/tradescanpro
#   ./scan_and_fix.sh suggest --out-dir /workspace/scan_output/tradescanpro > /workspace/scan_output/tradescanpro/fix_suggestions.md
#   ./scan_and_fix.sh fix --out-dir DIR --repo-dir PATH [--apply]

SCRIPT_NAME=$(basename "$0")

usage() {
  cat <<EOF
Usage:
  $SCRIPT_NAME scan --base-url URL [--out-dir DIR] [--max-pages N] [--respect-robots] [--sleep-seconds S]
  $SCRIPT_NAME suggest --out-dir DIR
  $SCRIPT_NAME fix --out-dir DIR --repo-dir PATH [--apply]

Options:
  --base-url URL          Root URL to scan (e.g., https://example.com)
  --out-dir DIR           Output directory (default: ./scan_output/<host>)
  --max-pages N           Max number of HTML pages to crawl (default: 500)
  --respect-robots        If set, excludes Disallow paths from robots.txt
  --sleep-seconds S       Delay between requests (float, default: 0.25)
  --seed-paths CSV       Comma-separated list of extra paths/URLs to seed (e.g., /auth,/auth/login)
  --include-disallow     Also seed robots.txt Disallow paths (for auditing), regardless of --respect-robots
  --repo-dir PATH         Local repository directory for optional automatic replacements
  --apply                 Actually mutate files during 'fix' (default is dry-run)

Notes:
  - This scanner uses curl only (no headless browser). It detects HTTP status issues and broken asset links, not runtime JS errors.
  - 'fix' mode can safely update references to final redirect URLs and switch http->https where valid.
EOF
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

abort() {
  echo "Error: $*" >&2
  exit 1
}

ensure_tools() {
  for tool in curl awk sed grep sort uniq tr tee; do
    command_exists "$tool" || abort "Required tool not found: $tool"
  done
}

url_origin() {
  # Prints scheme://host[:port]
  local u="$1"
  echo "$u" | sed -E 's#^([a-zA-Z][a-zA-Z0-9+.-]*://[^/]+).*#\1#'
}

url_scheme() {
  local u="$1"
  echo "$u" | sed -E 's#^([a-zA-Z][a-zA-Z0-9+.-]*).*$#\1#'
}

url_host() {
  local u="$1"
  # Strip scheme
  u=$(echo "$u" | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://##')
  # Host is up to first '/'
  echo "$u" | sed -E 's#/.*$##'
}

strip_query_fragment() {
  # Keep path only (drop ? and #)
  local u="$1"
  echo "$u" | sed -E 's/[?#].*$//'
}

base_path_dir() {
  # Given full URL, return its directory path (with leading '/'), e.g., '/a/b/'
  local u="$1"
  local path
  path=$(echo "$u" | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://[^/]+(.*)$#\1#')
  if [[ -z "$path" ]]; then
    echo "/"
    return
  fi
  # Remove query/fragment
  path=$(echo "$path" | sed -E 's/[?#].*$//')
  # If ends with '/', keep as directory
  if [[ "$path" == */ ]]; then
    echo "$path"
    return
  fi
  # Else drop last segment
  echo "$path" | sed -E 's#[^/]*$##'
}

normalize_path_stack() {
  local input="$1"
  # Collapse multiple slashes except leading '//' used for scheme-relative (not expected here)
  input=$(echo "$input" | sed -E 's#/{2,}#/#g')
  local IFS='/'
  read -ra parts <<< "$input"
  local -a stack=()
  local part
  for part in "${parts[@]}"; do
    case "$part" in
      ''|'.')
        ;;
      '..')
        if ((${#stack[@]} > 0)); then
          unset 'stack[${#stack[@]}-1]'
        fi
        ;;
      *)
        stack+=("$part")
        ;;
    esac
  done
  local result="/"
  if ((${#stack[@]} > 0)); then
    result="/$(IFS=/; echo "${stack[*]}")"
  fi
  echo "$result"
}

to_absolute_url() {
  # Convert possibly relative URL to absolute, based on base URL
  local base="$1"
  local ref="$2"

  # Trim surrounding whitespace and quotes
  ref=$(echo "$ref" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')
  # Remove one layer of surrounding quotes if present
  if [[ ${ref:0:1} == '"' && ${ref: -1} == '"' ]]; then
    ref="${ref:1:${#ref}-2}"
  elif [[ ${ref:0:1} == "'" && ${ref: -1} == "'" ]]; then
    ref="${ref:1:${#ref}-2}"
  fi

  # Skip empty or non-http refs
  [[ -z "$ref" ]] && return 1
  [[ "$ref" =~ ^(mailto:|tel:|javascript:|data:|blob:) ]] && return 1

  # Scheme-relative
  if [[ "$ref" == //* ]]; then
    local scheme
    scheme=$(url_scheme "$base")
    echo "$scheme:$ref"
    return 0
  fi

  # Absolute
  if [[ "$ref" =~ ^https?:// ]]; then
    echo "$ref"
    return 0
  fi

  local origin
  origin=$(url_origin "$base")

  # Root-relative
  if [[ "$ref" == /* ]]; then
    local path
    path=$(normalize_path_stack "$ref")
    echo "$origin$path"
    return 0
  fi

  # Relative to base directory
  local dir
  dir=$(base_path_dir "$base")
  local joined
  joined=$(normalize_path_stack "$dir/$ref")
  echo "$origin$joined"
}

is_same_host() {
  local a="$1" b="$2"
  local ha hb
  ha=$(url_host "$a")
  hb=$(url_host "$b")
  [[ "$ha" == "$hb" ]]
}

sleep_brief() {
  local s="$1"
  # support fractional seconds where possible
  python3 - "$s" <<'PY' 2>/dev/null || perl -e "select(undef,undef,undef,$s)" 2>/dev/null || sleep 1
import sys, time
time.sleep(float(sys.argv[1]))
PY
}

extract_links_and_assets() {
  # Reads HTML from stdin; outputs two streams via named pipes:
  # echo page-links and asset-links to files specified as args
  local page_base_url="$1"
  local pages_out="$2"
  local assets_out="$3"

  # Grep href/src and CSS url(…)
  # 1) href/src
  # 2) CSS url('…') and @import "…"
  local tmp_all tmp_html
  tmp_all=$(mktemp)
  tmp_html=$(mktemp)
  # Read stdin once into a temp file so we can parse multiple times
  cat - > "$tmp_html"

  # Build a skip list for link rel preconnect/dns-prefetch
  local tmp_skip
  tmp_skip=$(mktemp)
  # double-quoted
  grep -Eoi '<link[^>]+rel="(preconnect|dns-prefetch)"[^>]*href="[^"]+"' "$tmp_html" \
    | grep -Eoi 'href="[^"]+"' | sed -E 's/^href=//; s/^"|"$//g' >> "$tmp_skip" || true
  # single-quoted
  grep -Eoi "<link[^>]+rel='(preconnect|dns-prefetch)'[^>]*href='[^']+'" "$tmp_html" \
    | grep -Eoi "href='[^']+'" | sed -E "s/^href=//; s/^'|'$//g" >> "$tmp_skip" || true

  # Temporarily disable pipefail so empty grep results don't abort the script
  set +o pipefail
  # shellcheck disable=SC2002
  cat "$tmp_html" \
    | grep -Eoi -e 'href="[^\"]+"' -e 'src="[^\"]+"' -e "href='[^']+'" -e "src='[^']+'" \
    | sed -E -e 's/^(href|src)=//I' -e 's/^\"//; s/\"$//' -e "s/^'//; s/'$//" \
    | sed -E 's/^[[:space:]]+|[[:space:]]+$//g' \
    | grep -Fvx -f "$tmp_skip" \
    > "$tmp_all"

  # CSS urls
  # shellcheck disable=SC2002
  cat "$tmp_html" \
    | grep -Eoi -e 'url\(([^)]+)\)' -e '@import\s+url\(([^)]+)\)' -e '@import\s+\"[^\"]+\"' -e "@import\s+'[^']+'" \
    | sed -E -e 's/^.*url\(([^)]+)\).*$/\1/I' -e 's/^@import\s+\"([^\"]+)\"$/\1/I' -e "s/^@import\s+'([^']+)'$/\1/I" \
    | sed -E 's/^[[:space:]]+|[[:space:]]+$//g' \
    >> "$tmp_all"
  # Restore pipefail
  set -o pipefail

  # Filter out junk, make absolute, and classify pages vs assets
  while IFS= read -r raw; do
    [[ -z "$raw" ]] && continue
    # Skip anchors, mailto, javascript, data
    if [[ "$raw" =~ ^#|^(mailto:|tel:|javascript:|data:|blob:) ]]; then
      continue
    fi
    local abs
    if ! abs=$(to_absolute_url "$page_base_url" "$raw" 2>/dev/null); then
      continue
    fi
    # If same host and looks like a page (no extension or .html), treat as page
    local path_no_q
    path_no_q=$(strip_query_fragment "$abs")
    if is_same_host "$page_base_url" "$abs" && [[ ! "$path_no_q" =~ \.(css|js|mjs|jsx|ts|tsx|png|jpg|jpeg|gif|svg|webp|ico|bmp|mp4|webm|ogg|mp3|wav|woff|woff2|ttf|eot)(/)?$ ]]; then
      echo "$abs" >> "$pages_out"
    else
      echo "$abs" >> "$assets_out"
    fi
  done < "$tmp_all"

  rm -f "$tmp_all" "$tmp_html" "$tmp_skip"
}

fetch_url() {
  local url="$1" headers_out="$2" body_out="$3" http_info_out="$4" max_time="$5"
  # Fetch URL; capture headers and body; write curl -w info to file
  curl -sSL --max-time "$max_time" --retry 2 --retry-delay 1 \
    -A "Mozilla/5.0 (compatible; $SCRIPT_NAME/1.0)" \
    -D "$headers_out" -o "$body_out" \
    -w '%{http_code}\t%{content_type}\t%{url_effective}\t%{num_redirects}\n' \
    "$url" > "$http_info_out" || true
}

check_url_head() {
  local url="$1" http_info_out="$2" max_time="$3"
  # HEAD (or GET if HEAD fails) to get status without body
  # Try HEAD first
  local tmp_headers
  tmp_headers=$(mktemp)
  if curl -sSIL --max-time "$max_time" --retry 1 -A "Mozilla/5.0 (compatible; $SCRIPT_NAME/1.0)" "$url" -w '%{http_code}\t%{content_type}\t%{url_effective}\t%{num_redirects}\n' -o /dev/null > "$http_info_out" 2>/dev/null; then
    rm -f "$tmp_headers"
    return 0
  fi
  # Fallback to GET with range 0-0
  curl -sSL --max-time "$max_time" --retry 1 -A "Mozilla/5.0 (compatible; $SCRIPT_NAME/1.0)" -r 0-0 "$url" -w '%{http_code}\t%{content_type}\t%{url_effective}\t%{num_redirects}\n' -o /dev/null > "$http_info_out" || true
  rm -f "$tmp_headers"
}

parse_http_info() {
  # Input format: "<code> <content_type> <url_effective> <num_redirects>"
  local f="$1"
  awk -F '\t' '{code=$1; ct=$2; ue=$3; nr=$4; print code"|"ct"|"ue"|"nr}' "$f"
}

respect_disallow() {
  local base_url="$1" url_to_check="$2" robots_txt_file="$3"
  if [[ ! -s "$robots_txt_file" ]]; then
    return 0
  fi
  local origin
  origin=$(url_origin "$base_url")
  local path
  path=$(echo "$url_to_check" | sed -E "s#^$origin##")
  awk -v p="$path" 'BEGIN{IGNORECASE=1; disallow[0]=""} /^Disallow:/ {gsub(/\r/,"",$0); gsub(/Disallow:/, ""); gsub(/^\s+|\s+$/, ""); pats[++n]=$0} END{for(i=1;i<=n;i++){pat=pats[i]; if (pat=="" ) {continue}; if (index(p, pat)==1) {exit 1}} exit 0}' "$robots_txt_file"
}

scan_site() {
  ensure_tools

  local base_url="" out_dir="" max_pages=500 respect=0 sleep_seconds=0.25
  local seed_paths="" include_disallow=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --base-url)
        base_url="$2"; shift 2;;
      --out-dir)
        out_dir="$2"; shift 2;;
      --max-pages)
        max_pages="$2"; shift 2;;
      --respect-robots)
        respect=1; shift 1;;
      --sleep-seconds)
        sleep_seconds="$2"; shift 2;;
      --seed-paths)
        seed_paths="$2"; shift 2;;
      --include-disallow)
        include_disallow=1; shift 1;;
      *)
        echo "Unknown option for scan: $1" >&2; usage; exit 2;;
    esac
  done

  [[ -z "$base_url" ]] && abort "--base-url is required"
  if [[ -z "$out_dir" ]]; then
    local host
    host=$(url_host "$base_url")
    out_dir="./scan_output/$host"
  fi

  mkdir -p "$out_dir"

  local queue_file="$out_dir/queue.txt"
  local visited_file="$out_dir/visited.txt"
  local pages_csv="$out_dir/pages.csv"
  local assets_csv="$out_dir/assets.csv"
  local errors_csv="$out_dir/errors.csv"
  local redirects_csv="$out_dir/redirects.csv"
  local robots_txt="$out_dir/robots.txt"
  local sitemap_urls="$out_dir/sitemaps.txt"
  local discovered_pages="$out_dir/discovered_pages.txt"
  local discovered_assets="$out_dir/discovered_assets.txt"
  local assets_checked="$out_dir/assets_checked.txt"
  local crawl_log="$out_dir/crawl.log"

  : > "$queue_file"
  : > "$visited_file"
  : > "$pages_csv"
  : > "$assets_csv"
  : > "$errors_csv"
  : > "$redirects_csv"
  : > "$discovered_pages"
  : > "$discovered_assets"
  : > "$assets_checked"
  : > "$crawl_log"

  echo "type,parent_url,url,code,num_redirects,content_type,bytes,final_url" >> "$pages_csv"
  echo "type,parent_url,url,code,num_redirects,content_type,bytes,final_url" >> "$assets_csv"

  # Fetch robots.txt and find sitemaps
  local origin
  origin=$(url_origin "$base_url")
  curl -sS "$origin/robots.txt" -o "$robots_txt" || true
  grep -Ei '^Sitemap:\s*' "$robots_txt" | sed -E 's/^Sitemap:\s*//I' > "$sitemap_urls" || true
  # Always include the site's own sitemap.xml as a seed
  echo "$origin/sitemap.xml" >> "$sitemap_urls"
  sort -u "$sitemap_urls" -o "$sitemap_urls"

  # Seed queue with base URL
  echo "$base_url" >> "$queue_file"

  # Seed extra paths
  if [[ -n "$seed_paths" ]]; then
    IFS=',' read -r -a extra_seeds <<< "$seed_paths"
    for sp in "${extra_seeds[@]}"; do
      [[ -z "$sp" ]] && continue
      if [[ "$sp" =~ ^https?:// ]]; then
        echo "$sp" >> "$queue_file"
      else
        # treat as path
        local abs
        abs="$(url_origin "$base_url")$sp"
        echo "$abs" >> "$queue_file"
      fi
    done
  fi

  # Optionally seed Disallow paths from robots.txt for auditing
  if [[ "$include_disallow" -eq 1 && -s "$robots_txt" ]]; then
    awk 'BEGIN{IGNORECASE=1} /^Disallow:/ {gsub(/\r/,"",$0); p=$0; sub(/Disallow:/,"",p); gsub(/^\s+|\s+$/, "", p); if(p!="") print p}' "$robots_txt" \
      | while IFS= read -r d; do
          if [[ "$d" == /* ]]; then
            echo "$(url_origin "$base_url")$d"
          fi
        done >> "$queue_file"
  fi

  # Parse sitemap(s)
  if [[ -s "$sitemap_urls" ]]; then
    while IFS= read -r sm; do
      [[ -z "$sm" ]] && continue
      local tmp_sm
      tmp_sm=$(mktemp)
      curl -sSL "$sm" -o "$tmp_sm" || true
      # Parse <loc> entries and convert relative paths to absolute URLs
      grep -Eoi '<loc>[^<]+' "$tmp_sm" \
        | sed -E 's#</?loc>##g' \
        | tr -d '\r' \
        | sed -E 's/^[[:space:]]+|[[:space:]]+$//g' \
        | while IFS= read -r loc; do
            if [[ -z "$loc" ]]; then continue; fi
            if [[ "$loc" == /* ]]; then
              echo "$origin$loc"
            else
              echo "$loc"
            fi
          done >> "$discovered_pages" || true
      rm -f "$tmp_sm"
    done < "$sitemap_urls"
  fi

  # Merge discovered pages into queue (same host only)
  awk -v base="$base_url" 'BEGIN{IGNORECASE=1}
    {print $0}' "$discovered_pages" | while IFS= read -r p; do
    [[ -z "$p" ]] && continue
    if is_same_host "$base_url" "$p"; then
      echo "$p"
    fi
  done | sort -u >> "$queue_file"

  # Remove duplicates in queue
  sort -u "$queue_file" -o "$queue_file"

  local pages_count=0

  while true; do
    url=$(head -n 1 "$queue_file" || true)
    [[ -z "$url" ]] && break
    tail -n +2 "$queue_file" > "$queue_file.tmp" || :
    mv "$queue_file.tmp" "$queue_file"
    # Respect robots Disallow if requested
    if [[ "$respect" -eq 1 ]]; then
      if ! respect_disallow "$base_url" "$url" "$robots_txt"; then
        echo "Skip (robots Disallow): $url" | tee -a "$crawl_log"
        continue
      fi
    fi
    # Skip if visited
    if grep -Fxq "$url" "$visited_file"; then
      continue
    fi

    echo "$url" >> "$visited_file"
    ((pages_count++)) || true
    echo "[Page $pages_count] $url" | tee -a "$crawl_log"

    local tmp_headers tmp_body tmp_info
    tmp_headers=$(mktemp)
    tmp_body=$(mktemp)
    tmp_info=$(mktemp)

    fetch_url "$url" "$tmp_headers" "$tmp_body" "$tmp_info" 25
    local info
    info=$(parse_http_info "$tmp_info")
    local code ct final_url num_redirs
    code=$(echo "$info" | awk -F'|' '{print $1}')
    ct=$(echo "$info" | awk -F'|' '{print $2}')
    final_url=$(echo "$info" | awk -F'|' '{print $3}')
    num_redirs=$(echo "$info" | awk -F'|' '{print $4}')
    local bytes
    bytes=$(wc -c < "$tmp_body" | tr -d ' ')

    echo "page,,${url},${code},${num_redirs},${ct},${bytes},${final_url}" >> "$pages_csv"
    if [[ "$num_redirs" != "0" ]]; then
      echo "${url},${final_url}" >> "$redirects_csv"
    fi
    if [[ "$code" -ge 400 ]]; then
      echo "page,${url},${code}" >> "$errors_csv"
    fi

    # If HTML, extract links and assets
    if echo "$ct" | grep -qi 'text/html'; then
      local page_links assets_links
      page_links=$(mktemp)
      assets_links=$(mktemp)
      extract_links_and_assets "$final_url" "$page_links" "$assets_links" < "$tmp_body"

      # Append page links to queue (same host, not visited)
      if [[ -s "$page_links" ]]; then
        while IFS= read -r l; do
          [[ -z "$l" ]] && continue
          if is_same_host "$base_url" "$l"; then
            if ! grep -Fxq "$l" "$visited_file" 2>/dev/null && ! grep -Fxq "$l" "$queue_file" 2>/dev/null; then
              echo "$l" >> "$queue_file"
            fi
          fi
        done < <(sort -u "$page_links")
      fi

      # Check assets
      if [[ -s "$assets_links" ]]; then
        sort -u "$assets_links" | while IFS= read -r a; do
          [[ -z "$a" ]] && continue
          if grep -Fxq "$a" "$assets_checked"; then
            continue
          fi
          echo "$a" >> "$assets_checked"
          local a_info tmp_ai
          tmp_ai=$(mktemp)
          check_url_head "$a" "$tmp_ai" 20
          a_info=$(parse_http_info "$tmp_ai")
          local acode act afinal anr
          acode=$(echo "$a_info" | awk -F'|' '{print $1}')
          act=$(echo "$a_info" | awk -F'|' '{print $2}')
          afinal=$(echo "$a_info" | awk -F'|' '{print $3}')
          anr=$(echo "$a_info" | awk -F'|' '{print $4}')
          echo "asset,${url},${a},${acode},${anr},${act},,${afinal}" >> "$assets_csv"
          if [[ "$anr" != "0" ]]; then
            echo "${a},${afinal}" >> "$redirects_csv"
          fi
          if [[ "$acode" -ge 400 ]]; then
            echo "asset,${a},${acode}" >> "$errors_csv"
          fi
          # If JS and on same host or absolute, attempt to parse SPA route-like strings
          if echo "$act" | grep -qi 'javascript' || echo "$a" | grep -Eqi '\\.js(\?|$)'; then
            # Fetch small chunk to avoid huge downloads
            local tmp_js
            tmp_js=$(mktemp)
            curl -sSL --max-time 20 -A "Mozilla/5.0 (compatible; $SCRIPT_NAME/1.0)" -r 0-500000 "$afinal" -o "$tmp_js" || true
            # Heuristics: paths like "/auth", "/[a-z0-9-_/]+" possibly used by router
            # Ignore external hosts; we'll only add same-host routes
            grep -Eo '"/[a-zA-Z0-9_./-]+"' "$tmp_js" | tr -d '"' | sed -E 's/[?#].*$//' \
              | grep -E '^/' | sed -E 's#//+#/#g' | sort -u \
              | while IFS= read -r rp; do
                  local candidate
                  candidate="$(url_origin "$base_url")$rp"
                  if is_same_host "$base_url" "$candidate"; then
                    if ! grep -Fxq "$candidate" "$visited_file" 2>/dev/null && ! grep -Fxq "$candidate" "$queue_file" 2>/dev/null; then
                      echo "$candidate" >> "$queue_file"
                    fi
                  fi
                done
            rm -f "$tmp_js"
          fi
          rm -f "$tmp_ai"
          sleep_brief "$sleep_seconds"
        done
      fi

      rm -f "$page_links" "$assets_links"
    fi

    rm -f "$tmp_headers" "$tmp_body" "$tmp_info"

    # Stop if reached max
    if (( pages_count >= max_pages )); then
      echo "Reached --max-pages=$max_pages. Stopping." | tee -a "$crawl_log"
      break
    fi

    # Remove duplicates in queue occasionally
    sort -u "$queue_file" -o "$queue_file"

    sleep_brief "$sleep_seconds"
  done

  # Normalize redirects map
  if [[ -s "$redirects_csv" ]]; then
    sort -u "$redirects_csv" -o "$redirects_csv"
  fi

  echo "Scan complete. Output written to: $out_dir"
}

suggest_fixes() {
  ensure_tools
  local out_dir=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --out-dir) out_dir="$2"; shift 2;;
      *) echo "Unknown option for suggest: $1" >&2; usage; exit 2;;
    esac
  done
  [[ -z "$out_dir" ]] && abort "--out-dir is required"

  local pages_csv="$out_dir/pages.csv"
  local assets_csv="$out_dir/assets.csv"
  local errors_csv="$out_dir/errors.csv"
  local redirects_csv="$out_dir/redirects.csv"

  [[ -s "$pages_csv" ]] || abort "pages.csv not found or empty in $out_dir. Run scan first."
  [[ -s "$assets_csv" ]] || abort "assets.csv not found or empty in $out_dir. Run scan first."

  local host
  host=$(basename "$out_dir")

  echo "# Fix suggestions for $host"
  echo

  if [[ -s "$errors_csv" ]]; then
    echo "## Errors detected"
    echo
    echo "Broken pages or assets (HTTP >= 400):"
    echo
    awk -F',' '{print "- "$1" -> "$2" (code: "$3")"}' "$errors_csv" | sort -u
    echo
  else
    echo "No HTTP >= 400 errors detected."
    echo
  fi

  # Redirect updates
  if [[ -s "$redirects_csv" ]]; then
    echo "## Redirected URLs"
    echo
    echo "Update references from old URL to final URL to avoid runtime redirects:"
    echo
    awk -F',' '{print "- "$1" -> "$2}' "$redirects_csv" | sort -u
    echo
  fi

  # Mixed content (http assets on https pages)
  echo "## Mixed content candidates (http assets on https pages)"
  echo
  awk -F',' 'BEGIN{found=0}
    NR>1 && $1=="asset" {
      parent=$2; url=$3; code=$4; final=$8;
      if (parent ~ /^https:/ && url ~ /^http:/) {print "- "url" (parent: "parent")"; found=1}
    } END{if(found==0) print "- None found"}' "$assets_csv"
  echo

  # Suggestions section
  echo "## Suggestions"
  echo
  echo "- Replace references to redirected URLs with their final destinations."
  echo "- Switch http asset links to https if the resource is available over https."
  echo "- Fix or remove links to resources returning 404/410. Verify paths and filenames."
  echo "- Ensure the server returns proper 200/301 for canonical routes; avoid redirect chains (>1 hop)."
  echo

  # Replacement map (CSV) for automated fixes
  echo "## Replacement map (auto-fixable)"
  echo
  echo "The following pairs can be safely replaced in source code (left -> right):"
  echo
  if [[ -s "$redirects_csv" ]]; then
    awk -F',' '{print "- "$1" -> "$2}' "$redirects_csv" | sort -u
    echo
  fi
  echo "For http->https upgrades, validate availability first."
}

fix_repo() {
  ensure_tools
  local out_dir="" repo_dir="" apply=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --out-dir) out_dir="$2"; shift 2;;
      --repo-dir) repo_dir="$2"; shift 2;;
      --apply) apply=1; shift 1;;
      *) echo "Unknown option for fix: $1" >&2; usage; exit 2;;
    esac
  done
  [[ -z "$out_dir" ]] && abort "--out-dir is required"
  [[ -d "$repo_dir" ]] || abort "--repo-dir must be an existing directory"

  local redirects_csv="$out_dir/redirects.csv"
  local pages_csv="$out_dir/pages.csv"

  if [[ ! -s "$redirects_csv" ]]; then
    echo "No redirects.csv in $out_dir. Nothing to replace." >&2
  fi

  local -a targets
  # Target common web source files
  readarray -t targets < <(find "$repo_dir" -type f \( -iname '*.html' -o -iname '*.htm' -o -iname '*.js' -o -iname '*.jsx' -o -iname '*.ts' -o -iname '*.tsx' -o -iname '*.css' -o -iname '*.scss' -o -iname '*.md' -o -iname '*.json' \))

  echo "Planned replacements:"
  if [[ -s "$redirects_csv" ]]; then
    awk -F',' '{print "- "$1" -> "$2}' "$redirects_csv" | sort -u
  fi

  if [[ "$apply" -eq 0 ]]; then
    echo
    echo "Dry run. Use --apply to modify files."
    return 0
  fi

  # If repo is git, create a checkpoint
  if command_exists git && [[ -d "$repo_dir/.git" ]]; then
    (cd "$repo_dir" && git add -A && git commit -m "chore: pre-scan checkpoint [auto]" >/dev/null 2>&1 || true)
  fi

  # Apply redirect replacements
  if [[ -s "$redirects_csv" ]]; then
    while IFS=, read -r from to; do
      [[ -z "$from" || -z "$to" ]] && continue
      # Escape for sed
      local sfrom sto
      sfrom=$(printf '%s' "$from" | sed -e 's/[\/*.^$[]/\\&/g')
      sto=$(printf '%s' "$to" | sed -e 's/[\/*.^$[]/\\&/g')
      for f in "${targets[@]}"; do
        sed -i "s|$sfrom|$sto|g" "$f" || true
      done
    done < <(sort -u "$redirects_csv")
  fi

  echo "Applied replacements. Review changes in $repo_dir."
}

main() {
  [[ $# -lt 1 ]] && { usage; exit 2; }
  local cmd="$1"; shift || true
  case "$cmd" in
    scan) scan_site "$@" ;;
    suggest) suggest_fixes "$@" ;;
    fix) fix_repo "$@" ;;
    -h|--help|help) usage ;;
    *) echo "Unknown command: $cmd" >&2; usage; exit 2 ;;
  esac
}

main "$@"


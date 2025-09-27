import React from "react";

function upsertMetaTag(selector, attributes) {
  let element = document.head.querySelector(selector);
  if (!element) {
    element = document.createElement("meta");
    document.head.appendChild(element);
  }
  Object.entries(attributes).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      element.setAttribute(key, String(value));
    }
  });
}

function upsertLinkTag(rel, href, extraAttrs = {}) {
  if (!href) return;
  let element = document.head.querySelector(`link[rel="${rel}"]`);
  if (!element) {
    element = document.createElement("link");
    element.setAttribute("rel", rel);
    document.head.appendChild(element);
  }
  element.setAttribute("href", href);
  Object.entries(extraAttrs).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      element.setAttribute(key, String(value));
    }
  });
}

function removeExistingJsonLd(keyIdPrefix) {
  const existing = Array.from(document.head.querySelectorAll(`script[type="application/ld+json"]`))
    .filter((el) => el.id && el.id.startsWith(keyIdPrefix));
  existing.forEach((el) => el.remove());
}

function injectJsonLd(json, keyId) {
  const script = document.createElement("script");
  script.type = "application/ld+json";
  script.id = keyId;
  script.text = JSON.stringify(json);
  document.head.appendChild(script);
}

/**
 * SEO component for meta tag upserts and JSON-LD injection.
 *
 * Props:
 * - title: string
 * - description: string
 * - image: string (absolute or root-relative)
 * - imageAlt: string (optional)
 * - url: string (absolute)
 * - canonical: string (absolute). Fallbacks to window.location.href
 * - robots: string (e.g., "index,follow")
 * - jsonLd: object | object[] (inline JSON-LD)
 * - jsonLdUrls: string[] (fetch JSON-LD from public paths like "/structured/foo.jsonld")
 */
export default function SEO(props) {
  const {
    title,
    description,
    image,
    imageAlt,
    url,
    canonical,
    robots = "index,follow",
    jsonLd,
    jsonLdUrls,
  } = props;

  React.useEffect(() => {
    const siteName = "Trade Scan Pro";
    const resolvedUrl = url || (typeof window !== "undefined" ? window.location.href : undefined);
    const resolvedCanonical = canonical || resolvedUrl;
    const resolvedImage = image || "/logo.png";

    if (title) {
      document.title = title;
      upsertMetaTag('meta[property="og:title"]', { property: "og:title", content: title });
      upsertMetaTag('meta[name="twitter:title"]', { name: "twitter:title", content: title });
    }

    if (description) {
      upsertMetaTag('meta[name="description"]', { name: "description", content: description });
      upsertMetaTag('meta[property="og:description"]', { property: "og:description", content: description });
      upsertMetaTag('meta[name="twitter:description"]', { name: "twitter:description", content: description });
    }

    // Canonical
    if (resolvedCanonical) {
      upsertLinkTag("canonical", resolvedCanonical);
      upsertMetaTag('meta[property="og:url"]', { property: "og:url", content: resolvedCanonical });
      upsertMetaTag('meta[name="twitter:url"]', { name: "twitter:url", content: resolvedCanonical });
    }

    // Open Graph defaults
    upsertMetaTag('meta[property="og:type"]', { property: "og:type", content: "website" });
    upsertMetaTag('meta[property="og:site_name"]', { property: "og:site_name", content: siteName });
    upsertMetaTag('meta[property="og:locale"]', { property: "og:locale", content: "en_US" });
    upsertMetaTag('meta[property="og:image"]', { property: "og:image", content: resolvedImage });
    if (imageAlt || title) {
      upsertMetaTag('meta[property="og:image:alt"]', { property: "og:image:alt", content: imageAlt || title });
    }

    // Twitter card
    upsertMetaTag('meta[name="twitter:card"]', { name: "twitter:card", content: "summary_large_image" });
    upsertMetaTag('meta[name="twitter:site"]', { name: "twitter:site", content: "@TradeScanPro" });
    upsertMetaTag('meta[name="twitter:creator"]', { name: "twitter:creator", content: "@TradeScanPro" });
    upsertMetaTag('meta[name="twitter:image"]', { name: "twitter:image", content: resolvedImage });
    if (imageAlt || title) {
      upsertMetaTag('meta[name="twitter:image:alt"]', { name: "twitter:image:alt", content: imageAlt || title });
    }

    // Robots
    if (robots) {
      upsertMetaTag('meta[name="robots"]', { name: "robots", content: robots });
    }

    // Verification tokens via env
    const gsc = process.env.REACT_APP_GSC_VERIFICATION;
    if (gsc) upsertMetaTag('meta[name="google-site-verification"]', { name: "google-site-verification", content: gsc });
    const bing = process.env.REACT_APP_BING_VERIFICATION;
    if (bing) upsertMetaTag('meta[name="msvalidate.01"]', { name: "msvalidate.01", content: bing });
    const yandex = process.env.REACT_APP_YANDEX_VERIFICATION;
    if (yandex) upsertMetaTag('meta[name="yandex-verification"]', { name: "yandex-verification", content: yandex });

    // JSON-LD handling
    const keyPrefix = "jsonld-";
    removeExistingJsonLd(keyPrefix);

    const inline = Array.isArray(jsonLd) ? jsonLd : jsonLd ? [jsonLd] : [];
    inline.forEach((obj, index) => injectJsonLd(obj, `${keyPrefix}inline-${index}`));

    let aborted = false;
    async function fetchAndInject() {
      if (!jsonLdUrls || jsonLdUrls.length === 0) return;
      const fetches = jsonLdUrls.map(async (src, i) => {
        try {
          const res = await fetch(src, { credentials: "omit", cache: "no-cache" });
          if (!res.ok) return;
          const data = await res.json();
          if (!aborted) injectJsonLd(data, `${keyPrefix}remote-${i}`);
        } catch {}
      });
      await Promise.all(fetches);
    }
    fetchAndInject();

    return () => {
      aborted = true;
      removeExistingJsonLd(keyPrefix);
    };
  }, [title, description, image, imageAlt, url, canonical, robots, jsonLd, jsonLdUrls]);

  return null;
}


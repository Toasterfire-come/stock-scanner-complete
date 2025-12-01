## Stock Retrieval Module

### Quick Start
- `python -m stock_retrieval --max-tickers 50 --dry-run --json` — run a sample batch without DB writes and print summary stats.
- Add `--summary-json-path summaries/latest.json --summary-csv-path summaries/latest.csv` to persist structured run outputs.
- Use `--schedule` for continuous execution (default every 3 minutes, override with `--interval-minutes`).

### CLI Flags
- `--max-tickers`: limit processed symbols (default: all combined tickers).
- `--threads`: override worker pool size (env default `STOCK_RETRIEVAL_THREADS`, default 24).
- `--timeout` / `--symbol-timeout`: HTTP and per-symbol limits (seconds).
- `--dry-run`: skip database persistence; `--no-db` implies dry-run even if environment enables DB writes.
- `--no-proxies`: disable proxy usage; proxies auto-loaded from `working_proxies.json` otherwise.
- `--summary-json-path` / `--summary-csv-path`: file targets for structured metrics.
- `--log-level`: adjust logging verbosity; supports env override `STOCK_RETRIEVAL_LOG_LEVEL`.

### Operational Notes
- Combined ticker universe discovered from latest `backend/data/combined/combined_tickers_*.py`.
- Proxy pool auto-rotates on failures and records unhealthy entries for diagnostics (`ProxyPool.failures`).
- Executor metrics (success/failure counts, elapsed seconds, abort flag) emitted in summary under `executor_metrics`.
- Quality gate enforces required fields, timestamp freshness, and volume sanity; success ratio compared against configurable threshold (default 0.97).
- Persistence leverages Django ORM; ensuring `stockscanner_django.settings` is reachable and DB migrations are applied is prerequisite for live runs.

### Runbook Checklist
- **Pre-run**: validate `working_proxies.json`, confirm DB connectivity (`python manage.py check`), and ensure latest combined ticker file present.
- **During run**: tail `logs/stock_retrieval.log` for progress, monitor `executor_metrics.elapsed_seconds` and quality ratio.
- **Post-run**: archive JSON/CSV summaries, reconcile persistence errors (if any), and schedule rerun if quality ratio <97%.

### Testing & Benchmarks
- See `stock_retrieval_plan.md` for detailed unit/integration test inventory, performance targets (≤180s runtime, ≥97% quality pass), and soak test guidance.

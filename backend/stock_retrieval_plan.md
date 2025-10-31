## Stock Retrieval Script Plan

### Overview
- Build a production-ready stock retrieval script in `backend/` that leverages `yfinance` and supersedes `enhanced_stock_retrieval_working.py` by consolidating its data enrichment, resiliency, and database integration patterns.
- Target the combined ticker universe stored in `backend/data/combined/combined_tickers_*.py`, retrieving fresh market data within 180 seconds per full run.
- Achieve ≥97% success rate for tickers with complete datasets while maintaining high fidelity for persisted values in `stocks.Stock` and `stocks.StockPrice`.

### Success Metrics
- **Runtime**: Wall-clock time ≤180s for full combined ticker list on production hardware (document CPU, RAM, network specs).
- **Completion Accuracy**: ≥97% of submitted tickers return non-null price, volume, and 52-week range data (primary completeness score used in existing workflows).
- **Data Quality**: <0.5% of saved records require re-fetch due to validation failures (calculated via QC checks described below); zero database integrity errors.
- **Reliability**: Graceful retry handling results in <1% hard failures post retry window.

### Data Sources & Inputs
- Auto-load the most recent `COMBINED_TICKERS` module from `backend/data/combined/`, falling back to a deterministic default if newer modules are missing.
- Reference the CSV-based symbol filters (`flat-ui__data-*.csv`, `backend/data/full_run.csv`) only for QA audits—primary ticker universe is the combined file.
- Use runtime switches to support: `--max-tickers`, `--dry-run`, `--no-db`, `--use-proxies`, `--threads`, and `--timeout`.

### Key Components (modularized for maintainability)
- `config.py`: Centralize defaults (thread count, timeouts, retry policy, data quality thresholds, proxy file path, Django settings module).
- `ticker_loader.py`: Discovers latest combined ticker module, validates syntax, normalizes tickers (upper-case, deduped), partitions list for worker threads.
- `session_factory.py`: Prepares `requests.Session` and `yfinance` overrides, including proxy rotation and retry adapters seeded from `working_proxies.json`.
- `yfinance_client.py`: Thin wrapper around `yf.Ticker` operations with structured retries, caching (via `functools.lru_cache` or in-memory dict keyed by ticker/period), and typed response objects.
- `data_transformer.py`: Port `_safe_decimal`, `_extract_pe_ratio`, `_extract_dividend_yield`, historical price deltas, and volume analytics from `enhanced_stock_retrieval_working.py`, rewritten to pure functions to enable parallel use.
- `quality_gate.py`: Implements per-ticker validation (required fields present, value ranges sane, timestamps recent) and aggregates batch-level metrics for accuracy reporting.
- `db_writer.py`: Lazily initializes Django (`django.setup()`), upserts `Stock`, creates `StockPrice`, and surfaces database latency statistics; toggled off in dry-run mode.
- `executor.py`: Controls `ThreadPoolExecutor` lifecycle, dynamic throttling (reducing workers if error rate spikes), and instrumentation (progress logs, ETA, metrics export).
- `cli.py`: CLI entrypoint handling argument parsing, configuration merges, single-run or scheduler mode (3-minute cadence), and JSON/CSV export when requested.

### Execution Flow
1. **Bootstrap**: Parse CLI, load config, initialize logging directories under `backend/logs/`.
2. **Ticker Discovery**: `ticker_loader` locates latest combined ticker module, memoizes file hash, and returns an ordered, deduped list.
3. **Session Prep**: `session_factory` builds a shared `requests.Session` with proxy rotation (round-robin and health tracking) and attaches to `yfinance` internals.
4. **Concurrent Fetch**: `executor` shards tickers across worker pool (initial default 24 threads, auto-tunes based on CPU availability) and dispatches to `yfinance_client` with timeouts and retry envelopes (e.g., 3 attempts, exponential backoff up to 6s).
5. **Data Transformation**: Worker responses run through `data_transformer` producing normalized dict payload consistent with Django models.
6. **Quality Checks**: `quality_gate` validates required fields, calculates completeness score, and queues failures for retry or separate remediation queue.
7. **Persistence**: `db_writer` upserts validated payloads unless `--no-db`; optionally emit JSON snapshot to `backend/data/sample_run.json` for auditing.
8. **Metrics & Reporting**: Aggregate success/failure counts, runtime stats, per-step timings, and accuracy percentage; log to file and standard output, optionally push to Prometheus/OpenTelemetry hook.

### Performance Strategy (≤180s)
- Warm up `yfinance` by issuing lightweight metadata requests for first batch to reduce cold-start latency.
- Utilize batched historical calls via `yf.download` for large segments when beneficial (e.g., 50-ticker chunks for 1-day OHLC) and share results across workers.
- Monitor per-ticker latency; dynamically scale down threads if hitting Yahoo rate limits and scale up when latency drops below 200ms/ticker.
- Maintain an async retry queue handled by a smaller worker pool so that slow tickers do not block main throughput.
- Cache invariant reference data (e.g., company name, exchange) per ticker to avoid redundant network calls within a session.
- Enforce overall run timeout (e.g., `asyncio.wait_for` or wall-clock guard) to abort gracefully if approaching 170s and surface partial completion metrics.

### Data Quality & Accuracy Controls (≥97% completion)
- Require non-null `current_price`, `volume`, `fiftyTwoWeekHigh/Low`, and either `longName` or `shortName` for success classification.
- Cross-check `regularMarketTime` against run timestamp (max age 5 minutes) to prevent stale data acceptance.
- Validate numerical ranges (e.g., `volume` >0, `marketCap` >0 when present) and run anomaly detector comparing current price to previous close (±25% threshold triggers re-fetch).
- Implement multi-source fallback: if `ticker.info` fails, rely on `fast_info` (available in `yfinance`), then `yf.download` 1-day data.
- Persist retry diagnostics (ticker symbol, attempt count, error message) to `backend/logs/stock_retrieval_failures.log` for audit.

### Dependency & Configuration Notes
- Confirm `yfinance`, `pytz`, and `urllib3` versions align with `backend/requirements_production.txt`; update pinned versions as needed.
- Reuse proxy infrastructure from `enhanced_stock_retrieval_working.py` but abstract into health-checked pool with periodic verification.
- Ensure Django settings module (`stockscanner_django.settings`) loads lazily to prevent overhead during dry-run benchmarks.
- Include environment variable overrides for timeouts, thread counts, and log verbosity to support containerized deployments.

### Testing & Validation Plan
- **Unit Tests**: Cover each module (loader, transformer, quality gate) using fixtures derived from `enhanced_stock_retrieval_working.py` responses.
- **Integration Tests**: Run against 200-sample subset (via `--max-tickers 200`) using mock `yfinance` responses to simulate success/failure pathways.
- **Performance Tests**: Execute full combined list in staging, capture wall-clock and per-step timings; iterate thread/timeout tuning until 180s goal met.
- **Accuracy Verification**: Compare random 200 ticker sample against historical successful runs; assert ≥97% completeness metric.
- **Regression Suite**: Ensure database writes remain idempotent and do not duplicate `StockPrice` entries when run repeatedly within short intervals.

#### Detailed Test Inventory (current modules)
- **`ticker_loader`**: Unit tests for latest-file discovery, malformed ticker rejection, deterministic ordering, and `--max-tickers` truncation.
- **`yfinance_client`**: Mocked `yf.Ticker` to validate retry envelope, history fallbacks, `fast_info` usage, and captured error traces in `FetchResult`.
- **`executor`**: Fake fetcher to assert concurrency fan-out, runtime guard abort, and progress logging cadence under mixed success/failure scenarios.
- **`data_transformer`**: Numerical coercion checks (Decimal/int), price-change deltas across sparse histories, and dividend/PE extraction edge cases.
- **`quality_gate`**: Parameterised cases covering required-field enforcement, timestamp staleness (>300 s), and invalid volume handling with `QualityIssue` capture.
- **`db_writer`**: In-memory DB integration tests verifying update-or-create semantics, BigInteger coercion, and avoidance of duplicate `StockPrice` rows.
- **Reporting utilities**: Golden-file tests for JSON/CSV summary outputs ensuring executor + quality metrics persist as expected.

#### Performance & Acceptance Targets
- **Concurrency Benchmark**: With 24 worker threads, sustain ≤180 s total runtime for ≈5.5k combined tickers on production-equivalent hardware (document CPU/RAM/network baseline).
- **Quality Threshold**: Maintain ≥97 % quality-approved payloads per run; emit warning and retry batch if ratio dips below threshold for two consecutive runs.
- **Persistence Latency**: Keep database writes under 20 s per full batch (≤5 ms per `Stock` update, ≤3 ms per `StockPrice` insert) on target database engine.
- **Output Reporting**: Validate JSON/CSV summaries capture executor timing, success/failure counts, quality ratios, and persistence stats; ensure file rotation or overwrite strategy aligns with ops runbooks.
- **Scheduler Soak Test**: Exercise `--schedule` mode for 2 hours to observe memory stability, proxy rotation health, and resilience to intermittent Yahoo Finance outages.

### Rollout Steps
- Milestone 1: Implement modular structure with dry-run mode and validate against sample data.
- Milestone 2: Integrate proxy management, dynamic executor, and baseline metrics logging.
- Milestone 3: Connect to Django ORM, validate data quality checks, and attain ≥97% completeness on staging runs.
- Milestone 4: Performance tuning to hit ≤180s runtime; document hardware assumptions and bench results.
- Milestone 5: Enable scheduler integration and finalize operational playbook (monitoring, alert thresholds, failure remediation flow).

### Open Questions & Assumptions
- Confirm target hardware/network profile to validate 180s benchmark (current `enhanced_stock_retrieval_working.py` benchmarks needed for baseline).
- Determine whether combined ticker set is static per day or regenerated intra-day; if dynamic, incorporate checksum comparison to skip unchanged sets.
- Clarify reporting expectations for partial success (e.g., do we persist partial results when runtime guard triggers?).
- Validate that storing retry diagnostics in log files meets compliance requirements; if not, add dedicated database table for failure tracking.

### Next Steps
- Kick off Milestone 1 by scaffolding module structure within `backend/stock_retrieval/` and migrating shared utilities from the existing script.
- Schedule performance profiling session after initial implementation to calibrate thread counts and evaluate `yfinance` batching effectiveness.

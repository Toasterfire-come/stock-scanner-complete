# Operations Guide

## Environments & Secrets
- Use `/backend/.env.production.example` as a template.
- Set in a secrets manager (not `.env` on host):
  - DJANGO_ALLOWED_HOSTS, SECRET_KEY, FRONTEND_URL, CSRF_TRUSTED_ORIGINS
  - DB creds, EMAIL (SES) creds, PAYPAL creds + PAYPAL_WEBHOOK_ID
  - CRON_SECRET, API_KEY_PEPPER, SENTRY_DSN, ENVIRONMENT, RELEASE
  - FEATURE FLAGS: BACKEND_DOCS_ENABLED, API_KEYS_ENABLED, API_KEYS_BYPASS_*

## Build & Deploy (Docker Compose)
```bash
docker compose build
docker compose up -d
```
Backend: `http://localhost:8000` (dev) via compose; NGINX reverse proxy at `:80`/`:443`.

## Migrations
```bash
docker compose exec backend python manage.py migrate
```

## Admin Access
- Visit `/admin/` and login with superuser.
- Referral models, webhook events, and API keys are visible for moderation.

## Renewal Cron & Market Manager
- `market_hours_manager.py` runs with a daily 03:00 ET renewal trigger via `X-Cron-Secret`.
- Export `API_BASE_URL` and `CRON_SECRET` in the manager service/unit.

## Monitoring & Logging
- Sentry DSN recommended, set `SENTRY_DSN`, `ENVIRONMENT`, `RELEASE`.
- JSON logs enabled: set `JSON_LOGS=true`.
- Add Prometheus/Grafana: scrape NGINX and app metrics (extend as needed).

## Webhooks & Idempotency
- Set `PAYPAL_WEBHOOK_ID`. PayPal webhook verification persisted in `WebhookEvent`.
- Idempotency middleware stores `WebhookEvent` keyed by event ID/payload.

## Security
- Enforce HTTPS + HSTS via NGINX (`deploy/nginx/api.conf`).
- CORS: strict allow-list; API key flows can bypass rate limit/CORS via flags.
- Rate limiting: DRF throttles + middleware; WAF recommended in front.

## Runbooks
- Renewals failure:
  1) Check `/api/billing/process-renewals` with `X-Cron-Secret` (dry_run)
  2) Inspect `UserProfile.subscription_status` and `ReferralRedemption`
  3) Verify CRON_SECRET and market manager logs
- Webhook failures:
  1) Inspect `WebhookEvent` (status, payload hash)
  2) Verify PayPal verification; check `PAYPAL_WEBHOOK_ID`
  3) Re-deliver from provider; ensure endpoint returns 2xx for duplicates
- Data ingestion stale:
  1) Market manager logs; `enhanced_stock_retrieval_working.py`
  2) `/api/market-stats` latency/status
  3) Restart components; verify DB health

## SEO & Docs
- Hidden backend docs (404) unless `BACKEND_DOCS_ENABLED=true`.
- Sitemap lists SPA routes; update when adding pages.

## Backups & DR
- Nightly DB backups with encryption; test restore.
- Define RPO/RTO and test failover procedures.
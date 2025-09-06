import * as Sentry from '@sentry/react';

export function initSentry() {
  const dsn = process.env.REACT_APP_SENTRY_DSN;
  if (!dsn) return;
  Sentry.init({
    dsn,
    tracesSampler: (ctx) => {
      // Sample higher for vital transactions
      if (ctx.transactionContext && /login|checkout|load/i.test(ctx.transactionContext.name || '')) return 0.5;
      return 0.1;
    },
    replaysSessionSampleRate: 0.0,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({ maskAllText: true, blockAllMedia: true })
    ],
    environment: process.env.NODE_ENV,
    release: process.env.REACT_APP_VERSION || '1.0.0',
    beforeSend(event) {
      // Redact potential PII
      if (event.request) {
        if (event.request.headers) {
          delete event.request.headers['authorization'];
        }
        if (event.request.cookies) {
          delete event.request.cookies;
        }
      }
      if (event.user) {
        delete event.user.email;
        delete event.user.ip_address;
      }
      return event;
    }
  });
}


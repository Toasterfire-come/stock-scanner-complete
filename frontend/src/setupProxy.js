/**
 * CRA/CRACO dev proxy for backend API.
 *
 * In development, we prefer calling the API via relative paths ("/api/...").
 * This proxy forwards those requests to the configured backend URL.
 *
 * - Set REACT_APP_BACKEND_URL=http://localhost:8000 (or your backend) to override.
 * - Default is http://localhost:8000
 */
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  const target = (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '');

  app.use(
    '/api',
    createProxyMiddleware({
      target,
      changeOrigin: true,
      secure: false, // allow self-signed certs if you point to https in dev
      ws: true,
      logLevel: 'warn',
    })
  );
};

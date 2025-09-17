/**
 * Simple proxy server for production deployment
 * Routes frontend requests and proxies /api calls to backend
 */
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// Proxy middleware for API calls
const apiProxy = createProxyMiddleware({
  target: 'http://127.0.0.1:3002',
  changeOrigin: true,
  pathRewrite: {
    '^/api': '/api', // Keep /api path
  },
  onError: (err, req, res) => {
    console.error('Proxy Error:', err);
    res.status(502).json({ error: 'Backend service unavailable' });
  },
});

// Apply proxy to /api routes
app.use('/api', apiProxy);

// Serve static files from frontend build
app.use(express.static(path.join(__dirname, 'frontend', 'dist')));

// Handle all other routes by serving index.html (for SPA routing)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Proxy server running on port ${PORT}`);
  console.log(`Frontend: http://0.0.0.0:${PORT}`);
  console.log(`API proxy: http://0.0.0.0:${PORT}/api -> http://127.0.0.1:3002/api`);
});
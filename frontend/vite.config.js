/**
 * Vite Configuration
 *
 * This file configures the Vite build tool for the Anclora PDF2EPUB frontend.
 * It includes development server settings, build optimizations, and proxy configuration.
 */

import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default ({ mode }) => {
  // Load environment variables based on the current mode (development, production, etc.)
  const env = loadEnv(mode, process.cwd(), "");
  
  // Validate required environment variables
  const requiredEnvVars = [];
  const missingEnvVars = requiredEnvVars.filter(varName => !env[varName]);
  if (missingEnvVars.length > 0) {
    console.warn(`Warning: Missing environment variables: ${missingEnvVars.join(', ')}`);
  }
  
  return defineConfig({
    // React plugin configuration
    plugins: [react()],
    
    // Test configuration for Vitest
    test: {
      environment: "jsdom",
      setupFiles: ["./src/test-setup.ts"],
      globals: true,
    },
    server: {
      port: 5000,
      host: 'localhost', // Added missing comma
      // Define specific allowed hosts instead of using 'true' for better security
      allowedHosts: [
        'localhost',
        '127.0.0.1',
        // Add any other domains that need access to dev server here
      ],
      // Hot Module Replacement configuration
      hmr: {
        // Improve HMR reliability
        timeout: 120000,
        overlay: true,
      },
      
      // API proxy configuration
      proxy: {
        // Proxy all /api requests to the backend server
        "/api": {
          target: "http://127.0.0.1:5175",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path,
          // Proxy timeout settings
          timeout: 30000,
          // Log proxy redirects in development
          configure: (proxy, _options) => {
            // Error handling with detailed logging
            proxy.on("error", (err, req, res) => {
              const errorTime = new Date().toISOString();
              console.error(`[${errorTime}] Proxy error for ${req.method} ${req.url}:`, err);
              
              // Prevent connection hang on proxy error
              if (!res.headersSent) {
                res.writeHead(500, {
                  'Content-Type': 'application/json'
                });
                res.end(JSON.stringify({
                  error: 'Proxy error',
                  message: 'Cannot connect to backend server'
                }));
              }
            });
            
            // Request logging
            proxy.on("proxyReq", (proxyReq, req, _res) => {
              const timestamp = new Date().toISOString();
              console.log(`[${timestamp}] Proxying: ${req.method} ${req.url} → ${proxyReq.path}`);
            });
            
            // Response logging
            proxy.on("proxyRes", (proxyRes, req, _res) => {
              const timestamp = new Date().toISOString();
              console.log(`[${timestamp}] Received: ${proxyRes.statusCode} for ${req.method} ${req.url}`);
            });
          },
        }
      }
    },
    
    // Preview server configuration (for production build preview)
    preview: {
      port: 5000,
      host: true
    },
    
    // Build configuration
    build: {
      // Enable source maps for debugging production builds
      sourcemap: true,
      // Optimize chunk size and caching
      chunkSizeWarningLimit: 1000,
      // Minification options
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production', // Remove console logs in production
          drop_debugger: true
        }
      },
      // Code splitting configuration
      rollupOptions: {
        output: {
          // Split vendor libraries for better caching
          manualChunks: {
            vendor: ["react", "react-dom"],
            i18n: ["i18next", "react-i18next", "i18next-browser-languagedetector"]
          }
        }
      }
    },
    
    // Environment variable definitions
    define: {
      // Standardize on a single environment variable format
      "import.meta.env.VITE_API_URL": JSON.stringify(
        env.VITE_API_URL || "/api"
      ),
      // Add build timestamp for cache busting
      "import.meta.env.VITE_BUILD_TIMESTAMP": JSON.stringify(new Date().toISOString())
    }
  });
};




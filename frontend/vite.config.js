import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default ({ mode }) => {
  // Cargar variables de entorno
  const env = loadEnv(mode, process.cwd(), "");
  
  return defineConfig({
    plugins: [react()],
    test: {
      environment: "jsdom",
      setupFiles: ["./src/test-setup.ts"],
      globals: true,
    },
    server: {
      port: 5000,
      host: "0.0.0.0",
      allowedHosts: "all",
      proxy: {
        // Proxy all /api requests to the backend server
        "/api": {
          target: "http://localhost:3002",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path,
          // Log proxy redirects in development
          configure: (proxy, _options) => {
            proxy.on("error", (err, _req, _res) => {
              console.log("proxy error", err);
            });
            proxy.on("proxyReq", (proxyReq, req, _res) => {
              console.log("Proxying:", req.method, req.url, "→", proxyReq.path);
            });
          },
        }
      }
    },
    preview: {
      port: 5000,
      host: "0.0.0.0",
    },
    build: {
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ["react", "react-dom"],
            i18n: ["i18next", "react-i18next", "i18next-browser-languagedetector"]
          }
        }
      }
    },
    define: {
      // Standardize on a single environment variable format
      "import.meta.env.VITE_API_URL": JSON.stringify(
        env.VITE_API_URL || "/api"
      ),
    }
  });
};

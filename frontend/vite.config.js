import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default ({ mode }) => {
  // Cargar variables de entorno
  const env = loadEnv(mode, process.cwd(), '');

  return defineConfig({
    plugins: [react()],
    server: {
      port: 5178,
      host: '0.0.0.0',
    },
    preview: {
      port: 5178,
      host: '0.0.0.0',
    },
    build: {
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            i18n: ['i18next', 'react-i18next', 'i18next-browser-languagedetector']
          }
        }
      }
    },
    define: {
      'process.env.REACT_APP_API_URL': JSON.stringify(env.VITE_API_URL || env.REACT_APP_API_URL || 'http://localhost/api'),
    }
  });
};
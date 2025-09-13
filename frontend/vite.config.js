import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default ({ mode }) => {
  // Cargar variables de entorno
  const env = loadEnv(mode, process.cwd(), '');
  
  return defineConfig({
    plugins: [react()],
    server: {
      port: parseInt(env.PORT || 3003),
      host: '0.0.0.0',
    },
    define: {
      'process.env.REACT_APP_API_URL': JSON.stringify(env.REACT_APP_API_URL || 'http://localhost/api'),
    }
  });
};
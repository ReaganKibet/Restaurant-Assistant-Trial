import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Use .env variable for API base URL (fallback to localhost for dev)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:10000';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy API requests to FastAPI backend
      '/api': {
        target: API_BASE_URL,
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

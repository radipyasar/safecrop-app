import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// npm run dev  ->  http://localhost:5173 (opens in your browser by itself)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
  },
});

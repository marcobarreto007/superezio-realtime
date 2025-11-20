import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    }
  },
  server: {
    port: 3000,
    strictPort: true, // Falha se porta estiver ocupada
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // React core - ~140 kB
          'react-vendor': ['react', 'react-dom', 'react/jsx-runtime'],

          // Markdown rendering - ~200 kB
          'markdown': [
            'react-markdown',
            'react-syntax-highlighter',
          ],

          // Google APIs - ~150 kB (se usado)
          'google-apis': ['googleapis'],

          // Highlight.js - ~100 kB
          'highlight': ['highlight.js'],

          // Utilitários menores
          'utils': ['marked'],
        },
      },
    },
    // Aumentar limite para 600 kB (após split, cada chunk ficará < 500 kB)
    chunkSizeWarningLimit: 600,
  },
});
// frontend/vite.config.js
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  base: '/static/frontend/',
  build: {
    outDir: path.resolve(__dirname, '../static/frontend'),
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'src/index.html'),
      output: {
        entryFileNames: '[name].js',
        assetFileNames: '[name][extname]',
        chunkFileNames: '[name].js',
      },
    },
  },
});

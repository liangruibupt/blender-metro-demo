import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  build: {
    rollupOptions: { input: { main: 'index.html', film: 'film.html', watch: 'watch.html' } },
  },
  server: { strictPort: true },
  preview: { strictPort: true },
});

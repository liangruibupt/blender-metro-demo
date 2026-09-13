import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  appType: 'mpa',
  build: {
    manifest: true,
    rollupOptions: { input: {
      home: 'index.html',
      metro: 'metro/index.html', metroFilm: 'metro/film.html', metroWatch: 'metro/watch.html',
      optimus: 'optimus/index.html', optimusWatch: 'optimus/watch.html',
      legacyFilm: 'film.html', legacyWatch: 'watch.html',
      legacyOptimus: 'optimus.html', legacyOptimusWatch: 'optimus-watch.html',
    } },
  },
  server: { strictPort: true },
  preview: { strictPort: true },
});

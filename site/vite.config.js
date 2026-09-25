import { defineConfig } from 'vite';

// Base relativa ('./') funciona em qualquer subcaminho (ex.: https://usuario.github.io/analise-cftv-manutencoes/).
// Para forçar um caminho absoluto: BASE_PATH=/analise-cftv-manutencoes/ npm run build
export default defineConfig({
  base: process.env.BASE_PATH || './',
  build: { outDir: 'dist', assetsDir: 'assets', chunkSizeWarningLimit: 1200 },
});

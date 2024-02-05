import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { join } from 'node:path'
import legacy from '@vitejs/plugin-legacy'
import checker from 'vite-plugin-checker'

const resolve = (dir: string) => join(__dirname, dir)
const { CODESPACE_NAME } = process.env

export default defineConfig({
  plugins: [
    legacy({
      renderModernChunks: false,
    }),
    vue(),
    vuetify({
      autoImport: true,
    }),
    checker({
      typescript: true,
      vueTsc: true,
    }),
  ],
  resolve: {
    alias: {
      '@': resolve('src'),
    },
  },
  envPrefix: ['VUE_', 'NODE_'],
  build: {
    target: 'es2015',
  },
  server: {
    proxy: /* CODESPACE_NAME? */ {
      '^/api': {
        target: 'http://localhost:5000/api',
        changeOrigin: true,
      },
    },
    host: CODESPACE_NAME
      ? `${CODESPACE_NAME}-8888.preview.app.github.dev`
      : 'localhost',
    port: 8080,
  },
})

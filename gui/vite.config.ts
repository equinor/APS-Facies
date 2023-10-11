import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { join } from 'node:path'

const resolve = (dir: string) => join(__dirname, dir)
const { CODESPACE_NAME } = process.env

export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true,
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

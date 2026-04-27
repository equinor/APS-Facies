import { fileURLToPath, URL } from 'node:url'
import legacy from '@vitejs/plugin-legacy'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import checker from 'vite-plugin-checker'
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import { existsSync } from 'node:fs'

const isDocker = existsSync('/.dockerenv')
const { CODESPACE_NAME } = process.env

export default defineConfig({
  plugins: [
    legacy({
      renderModernChunks: false,
      targets: [
        'chrome >= 69', // RMS 14.2 uses Chromium 69
      ],
    }),
    vue({
      template: { transformAssetUrls },
    }),
    vuetify({
      autoImport: true,
      styles: {
        configFile: 'src/styles/settings.scss',
      },
    }),
    checker({
      vueTsc: true,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('src', import.meta.url)),
    },
    extensions: ['.js', '.json', '.jsx', '.mjs', '.ts', '.tsx', '.vue'],
  },
  envPrefix: ['VUE_', 'NODE_'],
  server: {
    allowedHosts: ['localhost', 'web'],
    proxy: /* CODESPACE_NAME? */ {
      // eslint-disable-next-line @typescript-eslint/naming-convention
      '^/api': {
        target: 'http://localhost:5000/api',
        changeOrigin: true,
      },
    },
    host: CODESPACE_NAME
      ? `${CODESPACE_NAME}-8888.preview.app.github.dev`
      : isDocker
        ? 'web'
        : 'localhost',
    port: 8080,
  },
})

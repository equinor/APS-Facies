'use strict'
const LodashModuleReplacementPlugin = require('lodash-webpack-plugin')

// Vue configurations
const isProduction = process.env.NODE_ENV === 'production'
const canParallelize = require('node:os').cpus().length > 1
const isDocker = require('node:fs').existsSync('/.dockerenv')

const assetsDir = 'static'

const { CODESPACE_NAME } = process.env
const API_PROTOCOL = process.env.VUE_APP_APS_PROTOCOL || 'http'
const API_SERVER = process.env.VUE_APP_APS_SERVER || '127.0.0.1'
const API_PORT = process.env.VUE_APP_APS_API_PORT || 5000

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */

module.exports = {
  assetsDir: assetsDir,
  runtimeCompiler: !isProduction,
  productionSourceMap: false,
  parallel: canParallelize,
  integrity: isProduction,

  css: {
    sourceMap: !isProduction,
  },

  chainWebpack: (config) => {
    config.module.rule('plot.ly').test(/\.js$/).use('IFY').loader('ify-loader')

    config.module
      .rule('ts')
      .use('ts-loader')
      .tap((options) => {
        options.appendTsSuffixTo = [/\.vue$/]
        return options
      })
  },
  devServer: {
    /* CODESPACE_NAME
      ? */
    proxy: isDocker
      ? `${API_PROTOCOL}://${API_SERVER}:${API_PORT}`
      : {
          '^/api': {
            target: 'http://localhost:5000/api',
            changeOrigin: true,
          },
        },
    // The port in Codespaces is the one used by NginX, and not the dev server
    // The reason, is that it is that URL that the browser sees.
    host: CODESPACE_NAME
      ? `${CODESPACE_NAME}-8888.preview.app.github.dev`
      : 'localhost:8080',
    port: 8080,
    // disableHostCheck: true,
  },

  // These dependencies contains various ECMA Script features, or syntax that are not supported by RMS 11
  // It uses Qt web browser, which, as of RMS 11, runs Chromium 56
  transpileDependencies: [
    // These dependencies contains spread operators
    'mathjs',
    'vuetify',
  ],

  configureWebpack: {
    plugins: [
      new LodashModuleReplacementPlugin({
        shorthands: false,
        cloning: true,
        currying: false,
        caching: false,
        collections: false,
        exotics: false,
        guards: false,
        metadata: false, // (requires currying)
        deburring: false,
        unicode: false,
        chaining: false,
        memoizing: false,
        coercions: false,
        flattening: false,
        paths: false,
        placeholders: false, // (requires currying)
      }),
    ],
  },

  lintOnSave: true,
}

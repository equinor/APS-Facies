'use strict'
const LodashModuleReplacementPlugin = require('lodash-webpack-plugin')

// Vue configurations
const isProduction = process.env.NODE_ENV === 'production'
const canParallelize = require('os').cpus().length > 1

const assetsDir = 'static'

const { CODESPACE_NAME } = process.env

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

  chainWebpack: config => {
    config.module
      .rule('plot.ly')
      .test(/\.js$/)
      .use('IFY')
      .loader('ify-loader')

    config.module
      .rule('ts')
      .use('ts-loader')
      .tap(options => {
        options.appendTsSuffixTo = [/\.vue$/]
        return options
      })
  },
  devServer: {
    proxy: /* CODESPACE_NAME
      ? */({
      '^/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }),
    // The port in Codespaces is the one used by NginX, and not the dev server
    // The reason, is that it is that URL that the browser sees.
    host: CODESPACE_NAME ? `${CODESPACE_NAME}-8888.preview.app.github.dev` : 'localhost:8080',
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

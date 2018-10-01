'use strict'
// Vue configurations
const isProduction = process.env.NODE_ENV === 'production'
const canParallelize = require('os').cpus().length > 1

const assetsDir = 'static'

module.exports = {
  assetsDir: assetsDir,
  runtimeCompiler: !isProduction,
  productionSourceMap: false,
  parallel: canParallelize,

  css: {
    sourceMap: !isProduction,
    modules: false,
    loaderOptions: {
      css: {
        minimize: isProduction,
      },
    }
  },

  lintOnSave: true,
}

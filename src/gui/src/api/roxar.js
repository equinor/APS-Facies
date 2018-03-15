'use strict';

/* eslint-disable camelcase */

(function (export_scope) {
  let rms = {}

  function callPythonFunction (code) {
    return new Promise((resolve, reject) => {
      // execute code, if successful call resolve with the result, otherwise reject

      // simple:
      alert(code)
      resolve()
    })
  }

  // utilities
  let uipy_handler = {
    get (target, propKey) {
      return function (...args) {
        let argstr = ''
        for (let i = 0, e = args.length; i < e; ++i) {
          if (i > 0) argstr += ', '
          argstr += "json.loads(r'" + JSON.stringify(args[i]) + "')"
        }
        return callPythonFunction('ui.' + propKey + '(' + argstr + ')')
      }
    }
  }
  rms.uipy = new Proxy({}, uipy_handler)

  export_scope.rms = rms
})(this)

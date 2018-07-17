'use strict'
// import Vue from 'vue'
import axios from 'axios'
const API_PROTOCOL = process.env.VUE_APP_APS_PROTOCOL || 'http'
const API_SERVER = process.env.VUE_APP_APS_SERVER || 'localhost'
const API_PORT = process.env.VUE_APP_APS_API_PORT || 5000

function callPythonFunction (code) {
  return new Promise((resolve, reject) => {
    // execute code, if successful call resolve with the result, otherwise reject

    // simple:
    axios.get(`${API_PROTOCOL}://${API_SERVER}:${API_PORT}/${code}`, {
      headers: {'Content-Type': 'text/html; charset=utf-8'}
    })
      .then(response => {
        resolve(response.data)
      })
  })
}

// utilities
// eslint-disable-next-line camelcase
let uipy_handler = {
  get (target, propKey) {
    return function (...args) {
      let argstr = ''
      for (let i = 0, e = args.length; i < e; ++i) {
        if (i > 0) argstr += ', '
        argstr += JSON.stringify(args[i])
      }
      return callPythonFunction('ui.' + propKey + '(' + argstr + ')')
    }
  }
}
export const rms = {
  uipy: new Proxy({}, uipy_handler)
}

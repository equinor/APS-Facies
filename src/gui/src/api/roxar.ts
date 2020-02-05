'use strict'
import axios from 'axios'
const API_PROTOCOL = process.env.VUE_APP_APS_PROTOCOL || 'http'
const API_SERVER = process.env.VUE_APP_APS_SERVER || '127.0.0.1'
const API_PORT = process.env.VUE_APP_APS_API_PORT || 5000

function callPythonFunction (code: string): Promise<JSON> {
  return new Promise((resolve, reject) => {
    // execute code, if successful call resolve with the result, otherwise reject

    // simple:
    axios.get(`${API_PROTOCOL}://${API_SERVER}:${API_PORT}/${code}`, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    })
      .then(response => {
        resolve(response.data)
      })
      .catch(reason => reject(reason))
  })
}

// utilities
const uipyHandler = {
  get (target: unknown, propKey: string): (...args: any[]) => Promise<JSON> {
    return function (...args: any[]): Promise<JSON> {
      let argstr = ''
      for (let i = 0, e = args.length; i < e; ++i) {
        if (i > 0) argstr += ', '
        argstr += JSON.stringify(args[i])
      }
      return callPythonFunction(`ui.${propKey}(${argstr})`)
    }
  }
}
export const rms = {
  uipy: new Proxy({}, uipyHandler)
}

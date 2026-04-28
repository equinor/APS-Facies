'use strict'

function callPythonFunction(method: string, parameters: string): Promise<JSON> {
  return new Promise((resolve, reject) => {
    // execute code, if successful call resolve with the result, otherwise reject

    // simple:
    fetch(`/${method}`, {
      method: 'POST',
      body: parameters,
      // eslint-disable-next-line @typescript-eslint/naming-convention
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
    })
      .then((response) => {
        response
          .json()
          .then((data) => resolve(data))
          .catch((reason) => reject(reason))
      })
      .catch((reason) => reject(reason))
  })
}

// utilities
const uipyHandler = {
  get(target: unknown, propKey: string): (...args: unknown[]) => Promise<JSON> {
    return function (...args: unknown[]): Promise<JSON> {
      let argstr = ''
      for (let i = 0, e = args.length; i < e; ++i) {
        if (i > 0) argstr += ', '
        argstr += JSON.stringify(args[i])
      }
      return callPythonFunction(`ui.${propKey}`, argstr)
    }
  },
}
export const rms = {
  uipy: new Proxy({}, uipyHandler),
}

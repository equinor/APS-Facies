import { RootState } from '@/store/typing'
import { createFmuVariables, createModel } from '@/utils/helpers/processing/export'
import { Module } from 'vuex'

const module: Module<{}, RootState> = {
  namespaced: true,

  actions: {
    createModelFileFromStore: (context): Promise<string> => {
      return new Promise((resolve, reject): void => {
        try {
          const xmlString = createModel(context)
          resolve(xmlString)
        } catch (error) {
          reject(error)
        }
      })
    },
    createGlobalVariables: (context): Promise<string> => {
      return new Promise((resolve, reject) => {
        try {
          const globalVariables = createFmuVariables(context)
          resolve(globalVariables)
        } catch (e) {
          reject(e)
        }
      })
    }
  }
}

export default module

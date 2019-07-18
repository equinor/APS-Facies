import { RootState } from '@/store/typing'
import { createModel } from '@/utils/helpers/processing/export'
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
    }
  }
}

export default module

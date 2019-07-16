import { createModel } from '@/utils/helpers/processing/export'

export default {
  namespaced: true,

  actions: {
    createModelFileFromStore: (context) => {
      return new Promise((resolve, reject) => {
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

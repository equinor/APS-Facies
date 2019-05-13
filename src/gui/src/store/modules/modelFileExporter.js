import { createModel } from '@/utils/helpers/processing/export'

export default {
  namespaced: true,

  actions: {
    createModelFileFromStore: ({ rootState, rootGetters }) => {
      return new Promise((resolve, reject) => {
        try {
          const xmlString = createModel({ rootState, rootGetters })
          resolve(xmlString)
        } catch (error) {
          reject(error)
        }
      })
    }
  }
}

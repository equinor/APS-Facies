import { RootState } from '@/store/typing'
import { createModel } from '@/utils/helpers/processing/export'
import { Module } from 'vuex'

const module: Module<Record<string, unknown>, RootState> = {
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
  },
  getters: {
    model: (state, getters, rootState, rootGetters): string => {
      try {
        return btoa(createModel({ rootState, rootGetters }))
      } catch (e) {
      }
      return ''
    },
  }
}

export default module

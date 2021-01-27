import { Module } from 'vuex'
import { RootState } from '@/store/typing'

import gaussianRandomFields from './gaussianRandomFields'

const module: Module<{}, RootState> = {
  namespaced: true,

  modules: {
    gaussianRandomFields,
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      await dispatch('gaussianRandomFields/fetch')
    }
  },

}

export default module

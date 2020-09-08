import { Dispatch } from 'vuex'
import rms from '@/api/rms'
import { makeSelectionModule } from '@/store/modules/parameters/utils'

export default {
  namespaced: true,

  modules: {
    fmuParameterListLocation: makeSelectionModule(() => rms.fmuParameterList()),
  },

  actions: {
    async fetch ({ dispatch }: { dispatch: Dispatch }): Promise<void> {
      await Promise.all([
        dispatch('fmuParameterListLocation/fetch'),
      ])
    }
  }
}

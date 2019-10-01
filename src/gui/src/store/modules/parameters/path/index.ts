import { Dispatch } from 'vuex'
import rms from '@/api/rms'
import project from './project'
import { makeSelectionModule } from '@/store/modules/parameters/utils'

export default {
  namespaced: true,

  modules: {
    project,
    fmuParameterListLocation: makeSelectionModule(() => rms.fmuParameterList()),
  },

  actions: {
    async fetch ({ dispatch }: { dispatch: Dispatch }): Promise<void> {
      await Promise.all([
        dispatch('project/fetch'),
        dispatch('fmuParameterListLocation/fetch'),
      ])
    }
  }
}

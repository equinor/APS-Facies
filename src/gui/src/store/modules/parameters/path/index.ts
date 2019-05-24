import { Dispatch } from 'vuex'
import project from './project'

export default {
  namespaced: true,

  modules: {
    project,
  },

  actions: {
    async fetch ({ dispatch }: { dispatch: Dispatch }): Promise<void> {
      await Promise.all([
        dispatch('project/fetch'),
      ])
    }
  }
}

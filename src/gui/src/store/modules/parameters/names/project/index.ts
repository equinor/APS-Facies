import rms from '@/api/rms'
import { RootState } from '@/store/typing'
import { ActionContext } from 'vuex'

import ProjectNameState from './typing'

export default {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    fetch: async ({ commit }: ActionContext<ProjectNameState, RootState>): Promise<void> => {
      commit('CURRENT', await rms.projectName())
    },
  },

  mutations: {
    CURRENT: (state: ProjectNameState, modelName: string): void => {
      state.selected = modelName
    },
  },
}

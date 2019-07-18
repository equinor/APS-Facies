import { Selectable } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'
import { Module } from 'vuex'

const module: Module<Selectable<string>, RootState> = {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    select: async ({ commit }, zone): Promise<void> => {
      commit('CURRENT', zone)
    },
  },

  mutations: {
    CURRENT: (state, zone): void => {
      state.selected = zone
    },
  },

  getters: {},
}

export default module

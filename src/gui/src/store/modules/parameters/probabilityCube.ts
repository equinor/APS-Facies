import rms from '@/api/rms'
import { StaticChoices } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'
import { Module } from 'vuex'

const module: Module<StaticChoices<string>, RootState> = {
  namespaced: true,

  state: {
    available: [],
  },

  actions: {
    fetch: async ({ commit, rootGetters }): Promise<void> => {
      const cubes = await rms.probabilityCubeParameters(rootGetters.gridModel)
      commit('AVAILABLE', cubes)
    }
  },

  mutations: {
    AVAILABLE: (state, cubes): void => {
      state.available = cubes
    },
  },

  getters: {},
}

export default module

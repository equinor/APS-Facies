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
    async fetch ({ commit, rootGetters }): Promise<void> {
      // TODO: Use 'fetchParameterHelper' to automatically chose the parameter?
      const params = await rms.trendParameters(rootGetters.gridModel)
      commit('AVAILABLE', params)
    },
  },

  mutations: {
    AVAILABLE (state, params): void {
      state.available = params
    },
  },
}

export default module

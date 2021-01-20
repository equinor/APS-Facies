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
    async fetch ({ dispatch }): Promise<void> {
      // TODO: Use 'fetchParameterHelper' to automatically chose the parameter?
      await dispatch('refresh')
    },
    refresh: async ({ commit, rootGetters }): Promise<void> => {
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

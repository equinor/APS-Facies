import api from '@/api/rms'
import { Maybe } from '@/utils/typing'
import { Module } from 'vuex'
import { FmuState } from '@/store/modules/parameters/typing'
import { RootState } from '@/store/typing'

const module: Module<FmuState, RootState> = {
  namespaced: true,

  state: {
    maxDepth: null,
  },

  actions: {
    async fetch ({ dispatch, rootGetters }, value: Maybe<number> = undefined): Promise<void> {
      if (value && value !== 0) {
        dispatch('set', value)
      } else {
        // @ts-ignore
        const [x, y, z] = await api.gridSize(rootGetters.gridModel)
        dispatch('set', z)
      }
    },
    set ({ commit }, value: number) {
      commit('SET', value)
    },
  },

  mutations: {
    SET (state, value) {
      state.maxDepth = value
    },
  },
}

export default module

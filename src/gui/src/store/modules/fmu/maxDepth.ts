import GridModel from '@/utils/domain/gridModel'
import { FmuLayersState } from './typing'
import { Maybe, Optional } from '@/utils/typing'
import { Module } from 'vuex'
import { RootState } from '@/store/typing'

const module: Module<FmuLayersState, RootState> = {
  namespaced: true,

  state: {
    value: null,
  },

  actions: {
    async fetch ({ dispatch, rootGetters }, value: Maybe<number> = undefined): Promise<void> {
      if (value && value !== 0) {
        await dispatch('set', value)
      } else {
        const grid: Optional<GridModel> = rootGetters['gridModels/current']
        if (grid) {
          await dispatch('set', grid.dimension.z)
        }
      }
    },

    async populate ({ dispatch }, { value }): Promise<void> {
      await dispatch('set', value)
    },

    async set ({ commit }, value: number): Promise<void> {
      commit('SET', value)
    },
  },

  mutations: {
    SET (state, value) {
      state.value = value
    },
  },
}

export default module

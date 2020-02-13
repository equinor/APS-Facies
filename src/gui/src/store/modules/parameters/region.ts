import rms from '@/api/rms'

import { SelectableChoice } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'
import { Module } from 'vuex'

const module: Module<SelectableChoice<string>, RootState> = {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: async ({ state, commit, dispatch }, regionParameter): Promise<void> => {
      if (state.available.includes(regionParameter)) {
        commit('CURRENT', regionParameter)
        await dispatch('regions/use', { use: !!regionParameter }, { root: true })

        await dispatch('facies/global/refresh', undefined, { root: true })
      } else {
        throw new Error(`Selected regionParam ( ${regionParameter} ) is not present int the current project

Tip: RegionParamName in the APS model File must be one of { ${state.available.join()} }`)
      }
    },
    fetch: async ({ commit, dispatch }): Promise<void> => {
      commit('CURRENT', null)
      await dispatch('refresh')
    },
    refresh: async ({ commit, rootGetters }): Promise<void> => {
      commit('AVAILABLE', await rms.regionParameters(rootGetters.gridModel))
    },
  },

  mutations: {
    AVAILABLE: (state, regionParameters): void => {
      state.available = regionParameters
    },
    CURRENT: (state, regionParameter): void => {
      state.selected = regionParameter
    },
  },
}

export default module

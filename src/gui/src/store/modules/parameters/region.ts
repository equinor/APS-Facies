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
    select: ({ state, commit, dispatch }, regionParameter): Promise<string> => {
      return new Promise((resolve, reject) => {
        if (state.available.includes(regionParameter)) {
          commit('CURRENT', regionParameter)
          dispatch('regions/use', { use: !!regionParameter }, { root: true })
            .then(() => {
              resolve(regionParameter)
            })
            .catch(error => {
              reject(error)
            })
        } else {
          reject(new Error(`Selected regionParam ( ${regionParameter} ) is not present int the current project

Tip: RegionParamName in the APS model File must be one of { ${state.available.join()} }`))
        }
      })
    },
    fetch: async ({ commit, rootGetters }): Promise<void> => {
      commit('CURRENT', null)
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

  getters: {},
}

export default module

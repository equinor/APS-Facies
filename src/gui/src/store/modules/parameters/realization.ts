import Vue from 'vue'
import rms from '@/api/rms'

import { Module } from 'vuex'
import { SelectableChoice } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'

import { DEFAULT_FACIES_REALIZATION_PARAMETER_NAME } from '@/config'

const module: Module<SelectableChoice<string>, RootState> = {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: async ({ commit }, parameter): Promise<void> => {
      commit('CURRENT', parameter)
    },
    fetch: async ({ commit, rootGetters }): Promise<string[]> => {
      commit('CURRENT', DEFAULT_FACIES_REALIZATION_PARAMETER_NAME)
      const discreteParameters = await rms.realizationParameters(rootGetters.gridModel)
      commit('AVAILABLE', discreteParameters)
      return discreteParameters
    },
  },

  mutations: {
    AVAILABLE: (state, parameters): void => {
      Vue.set(state, 'available', parameters)
    },
    CURRENT: (state, parameter): void => {
      state.selected = parameter
    },
  },

  getters: {},
}

export default module
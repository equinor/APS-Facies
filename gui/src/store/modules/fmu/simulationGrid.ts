import Vue from 'vue'
import { Module } from 'vuex'

import { DEFAULT_FMU_SIMULATION_GRID_NAME } from '@/config'

import { RootState } from '@/store/typing'
import { SimulationGridModelsState } from './typing'

const module: Module<SimulationGridModelsState, RootState> = {
  namespaced: true,

  state: {
    current: null,
  },

  actions: {
    select: async ({ commit }, gridModel: string): Promise<void> => {
      commit('CURRENT', gridModel)
    },

    set: async ({ dispatch }, gridModel: string): Promise<void> => dispatch('select', gridModel),

    fetch: async ({ dispatch }): Promise<void> => {
      await dispatch('select', DEFAULT_FMU_SIMULATION_GRID_NAME)
    },

    populate: async ({ dispatch }, { current }: SimulationGridModelsState): Promise<void> => {
      await dispatch('select', current)
    },
  },

  mutations: {
    CURRENT: (state, selectedGridModel: string): void => {
      Vue.set(state, 'current', selectedGridModel)
    },
    AVAILABLE: (state, gridModels): void => {
      Vue.set(state, 'available', gridModels)
    },
  },
}

export default module

import rms from '@/api/rms'
import { GridModel, GridModelsState } from '@/store/modules/gridModels/types'
import { RootState } from '@/store/typing'
import Vue from 'vue'
import { ActionTree, Module, MutationTree } from 'vuex'

const parametersDependentOnGrid = [
  'region',
  'blockedWell',
  'blockedWellLog',
  'rmsTrend',
  'probabilityCube',
  'grid',
  'realization',
]

const state: GridModelsState = {
  available: [],
  current: null,
}

const actions: ActionTree<GridModelsState, RootState> = {
  select: async ({ state, commit, dispatch }, gridModel: GridModel) => {
    if (state.available.includes(gridModel)) {
      commit('CURRENT', gridModel)
      await dispatch('zones/fetch', null, { root: true })
      await Promise.all(parametersDependentOnGrid.map(param => dispatch(`parameters/${param}/fetch`, undefined, { root: true })))
      // This takes quite a bit more time, and is not worth waiting for, as the rough estimates earlier are good enough for now
      // Hence no `await`
      dispatch('parameters/grid/simBox/fetch', false, { root: true })
    } else {
      throw new Error(`Selected grid model ( ${gridModel} ) is not present in the current project.

Tip: GridModelName in the APS model file must be one of { ${state.available.join()} }`)
    }
  },
  fetch: async ({ commit }): Promise<void> => {
    const gridModels = await rms.gridModels()
    commit('AVAILABLE', gridModels)
  }
}

const mutations: MutationTree<GridModelsState> = {
  CURRENT: (state, selectedGridModel): void => {
    Vue.set(state, 'current', selectedGridModel)
  },
  AVAILABLE: (state, gridModels): void => {
    state.available = gridModels
  },
}

const gridModels: Module<GridModelsState, RootState> = {
  namespaced: true,
  state,
  actions,
  mutations,
}

export default gridModels

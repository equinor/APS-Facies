import { DEFAULT_CREATE_FMU_GRID, DEFAULT_RUN_FMU_MODE, DEFAULT_RUN_ONLY_FMU_UPDATE } from '@/config'
import { makeOption, populateState } from '@/store/utils'
import { Module } from 'vuex'

import { RootState } from '@/store/typing'
import { FmuState } from './typing'
import maxDepth from './maxDepth'
import simulationGrid from './simulationGrid'

const module: Module<FmuState, RootState> = {
  namespaced: true,

  modules: {
    maxDepth,
    runFmuWorkflows: makeOption(DEFAULT_RUN_FMU_MODE, [true, false]),
    onlyUpdateFromFmu: makeOption(DEFAULT_RUN_ONLY_FMU_UPDATE, [true, false]),
    create: makeOption(DEFAULT_CREATE_FMU_GRID, [true, false]),
    simulationGrid,
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      await dispatch('simulationGrid/fetch')
    },

    async populate (context, options: FmuState): Promise<void> {
      await populateState(context, options)
    }
  },
}

export default module
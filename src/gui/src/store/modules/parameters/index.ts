import { Module } from 'vuex'
import ParametersState from '@/store/modules/parameters/typing'
import { RootState } from '@/store/typing'

import zone from '@/store/modules/parameters/zone'
import region from '@/store/modules/parameters/region'
import blockedWell from '@/store/modules/parameters/blockedWell'
import blockedWellLog from '@/store/modules/parameters/blockedWellLog'
import rmsTrend from '@/store/modules/parameters/rmsTrend'
import probabilityCube from '@/store/modules/parameters/probabilityCube'
import grid from '@/store/modules/parameters/grid'
import realization from '@/store/modules/parameters/realization'
import names from '@/store/modules/parameters/names'
import debugLevel from '@/store/modules/parameters/debugLevel'
import maxAllowedFractionOfValuesOutsideTolerance from '@/store/modules/parameters/maxAllowedFractionOfValuesOutsideTolerance'
import toleranceOfProbabilityNormalisation from '@/store/modules/parameters/toleranceOfProbabilityNormalisation'

const module: Module<ParametersState, RootState> = {
  namespaced: true,

  modules: {
    zone,
    region,
    blockedWell,
    blockedWellLog,
    rmsTrend,
    probabilityCube,
    grid,
    realization,
    names,
    debugLevel,
    maxAllowedFractionOfValuesOutsideTolerance,
    toleranceOfProbabilityNormalisation,
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      await Promise.all([
        dispatch('path/fetch'),
        dispatch('names/workflow/fetch'),
        dispatch('names/project/fetch'),
        dispatch('maxAllowedFractionOfValuesOutsideTolerance/fetch'),
        dispatch('toleranceOfProbabilityNormalisation/fetch'),
      ])
    }
  },
}

export default module

import rms from '@/api/rms'
import { GridModelsState } from '@/store/modules/gridModels/types'
import { RootState } from '@/store/typing'
import APSTypeError from '@/utils/domain/errors/type'
import GridModel, { GridModelConfiguration, GridModelSerialization } from '@/utils/domain/gridModel'
import { ID } from '@/utils/domain/types'
import { identify, isUUID } from '@/utils/helpers'
import { Optional } from '@/utils/typing'
import Vue from 'vue'
import { Module } from 'vuex'

const parametersDependentOnGrid = [
  'region',
  'blockedWell',
  'blockedWellLog',
  'rmsTrend',
  'probabilityCube',
  'grid',
  'realization',
]

const gridModels: Module<GridModelsState, RootState> = {
  namespaced: true,

  state: {
    available: {},
    current: null,
  },

  actions: {
    select: async ({ state, commit, dispatch, getters }, gridModel: GridModel | ID | string): Promise<void> => {
      const gridModels = getters.names
      const _gridModel = gridModel instanceof GridModel
        ? gridModel
        : isUUID(gridModel)
          ? state.available[`${gridModel}`]
          : Object.values(state.available).find(model => model.name === gridModel)
      if (!_gridModel) throw new APSTypeError(`The grid model, ${gridModel} does not exist`)

      if (gridModels.includes(_gridModel.name)) {
        commit('CURRENT', _gridModel)
        await dispatch(`panels/${_gridModel ? 'open' : 'close'}`, 'selection', { root: true })
        await dispatch('zones/fetch', null, { root: true })
        await Promise.all(parametersDependentOnGrid.map(param => dispatch(`parameters/${param}/fetch`, undefined, { root: true })))
        await dispatch('copyPaste/copy', null, { root: true })
        // This takes quite a bit more time, and is not worth waiting for, as the rough estimates earlier are good enough for now
        // Hence no `await`
        dispatch('parameters/grid/simBox/fetch', false, { root: true })
      } else {
        throw new Error(`Selected grid model ( ${_gridModel.name} ) is not present in the current project.

Tip: GridModelName in the APS model file must be one of { ${gridModels.join()} }`)
      }
    },
    populate: async ({ commit }, gridModels: (GridModelSerialization | GridModelConfiguration)[]): Promise<void> => {
      commit('AVAILABLE', identify(gridModels.map(conf => new GridModel(conf))))
    },
    fetch: async ({ dispatch }): Promise<void> => {
      const gridModels = (await rms.gridModels())
        .map((conf, index): GridModelConfiguration => {
          return {
            ...conf,
            order: index,
          }
        })
      await dispatch('populate', gridModels)
    }
  },

  mutations: {
    CURRENT: (state, selectedGridModel: Optional<GridModel>): void => {
      Vue.set(state, 'current', selectedGridModel ? selectedGridModel.id : selectedGridModel)
    },
    AVAILABLE: (state, gridModels): void => {
      Vue.set(state, 'available', gridModels)
    },
  },

  getters: {
    names (state): string[] {
      return Object.values(state.available)
        .sort((a, b): number => a.order - b.order)
        .map((model): string => model.name)
    }
  },
}

export default gridModels

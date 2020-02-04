import Vue from 'vue'
import Vuex, { Store } from 'vuex'

import copyPaste from '@/store/modules/copyPaste'
import message from '@/store/modules/message'
import panels from '@/store/modules/panels'
import gridModels from '@/store/modules/gridModels'
import zones from '@/store/modules/zones'
import regions from '@/store/modules/regions'
import facies from '@/store/modules/facies'
import gaussianRandomFields from '@/store/modules/gaussianRandomFields'
import truncationRules from '@/store/modules/truncationRules'
import parameters from '@/store/modules/parameters'
import constants from '@/store/modules/constants'
import options from '@/store/modules/options'
import modelFileLoader from '@/store/modules/modelFileLoader'
import modelFileExporter from '@/store/modules/modelFileExporter'
import fmu from '@/store/modules/fmu'

import { RootState } from '@/store/typing'
import { ID } from '@/utils/domain/types'
import { Optional } from '@/utils/typing'
import { Identified, SimulationSettings } from '@/utils/domain/bases/interfaces'

import Zone, { Region } from '@/utils/domain/zone'
import { GaussianRandomField } from '@/utils/domain'
import GlobalFacies from '@/utils/domain/facies/global'
import Facies from '@/utils/domain/facies/local'
import BaseItem from '@/utils/domain/bases/baseItem'
import TruncationRule from '@/utils/domain/truncationRule/base'

import migrate from '@/store/utils/migration'
import {
  defaultSimulationSettings,
  getParameters,
  hasCurrentParents,
  resolve,
  sortAlphabetically,
} from '@/utils'
import { hasOwnProperty } from '@/utils/helpers'

Vue.use(Vuex)

const store: Store<RootState> = new Vuex.Store({
  // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
  // @ts-ignore
  state: {
    version: '1.2.0',
    _loaded: {
      value: false,
      loading: false,
    },
    _loading: {
      value: false,
      message: '',
    },
  },

  strict: process.env.NODE_ENV !== 'production',

  modules: {
    copyPaste,
    message,
    panels,
    gridModels,
    zones,
    regions,
    facies,
    fmu,
    gaussianRandomFields,
    truncationRules,
    parameters,
    constants,
    options,
    modelFileLoader,
    modelFileExporter,
  },

  actions: {
    async fetch ({ dispatch, commit, getters }): Promise<void> {
      if (getters.mayLoadParameters) {
        commit('LOADING_PARAMETERS')
        await Promise.all([
          dispatch('gridModels/fetch'),
          dispatch('constants/fetch'),
          dispatch('truncationRules/fetch'),
          dispatch('parameters/fetch'),
          dispatch('fmu/fetch'),
        ])
        commit('FINISHED')
      }
    },
    async refresh ({ commit, dispatch, getters }, message): Promise<void> {
      if (!getters.loading) {
        commit('LOADING', { message })
        await Promise.all([
          dispatch('gridModels/refresh'),
        ])
        commit('LOADING', { loading: false })
      }
    },
    async populate ({ dispatch, state }, data): Promise<void> {
      // eslint-disable-next-line @typescript-eslint/no-use-before-define
      resetState()
      await dispatch('startLoading')
      data = await migrate(data, state.version)
      try {
        await dispatch('fetch')

        // Grid model
        await dispatch('gridModels/populate', Object.values(data.gridModels.available))
        if (data.gridModels.current) {
          await dispatch('gridModels/select', data.gridModels.current)
        }

        // Parameters
        for (const parameter of getParameters(data.parameters)) {
          const { selected }: { selected?: string} = resolve(parameter, data.parameters)
          if (selected) {
            await dispatch(`parameters/${parameter.replace('.', '/')}/select`, selected)
          } else if (parameter === 'grid') {
            await dispatch('parameters/grid/populate', data.parameters.grid)
            await dispatch('parameters/grid/simBox/populate', data.parameters.grid.simBox)
          } else {
            // Ignored
          }
        }

        // Options
        await dispatch('options/populate', data.options)

        // FMU settings
        await dispatch('fmu/populate', data.fmu)

        // Zones
        await dispatch('zones/populate', { zones: Object.values(data.zones.available) })
        if (data.zones.current) {
          await dispatch('zones/current', { id: data.zones.current })
        }

        // Regions
        await dispatch('regions/use', { use: data.regions.use, fetch: false })
        if (data.regions.current) {
          await dispatch('regions/current', { id: data.regions.current })
        }

        // Color library
        await dispatch('constants/faciesColors/populate', data.constants.faciesColors)

        // Facies
        await dispatch('facies/global/populate', Object.values(data.facies.global.available))
        await dispatch('facies/populate', Object.values(data.facies.available))
        await dispatch('facies/groups/populate', Object.values(data.facies.groups.available))
        await dispatch('facies/populateConstantProbability', data.facies.constantProbability)

        // Gaussian Random Fields
        await dispatch('gaussianRandomFields/crossSections/populate', Object.values(data.gaussianRandomFields.crossSections.available))
        await dispatch('gaussianRandomFields/populate', Object.values(data.gaussianRandomFields.available))

        // Truncation rules
        await dispatch('truncationRules/populate', data.truncationRules)

        // Reopen the different panels
        await dispatch('panels/populate', data.panels)
        // Make sure the available data is up to date
        await dispatch('refresh')
      } finally {
        await dispatch('finnishLoading')
      }
    },
    async startLoading ({ commit }): Promise<void> {
      commit('LOADING', { loading: true, message: 'Loading job. Please wait.' })
    },
    async finnishLoading ({ commit }): Promise<void> {
      commit('LOADING', { loading: false })
    }
  },

  mutations: {
    RESET: (state, initial): void => {
      Object.assign(state, initial)
    },
    FINISHED: (state): void => {
      state._loaded.value = true
      state._loaded.loading = false
    },
    LOADING_PARAMETERS: (state): void => {
      state._loaded.loading = true
    },
    LOADING: (state, { loading = true, message = '' }: { loading?: boolean, message?: string } = {}): void => {
      state._loading.value = loading
      state._loading.message = message
    }
  },

  getters: {
    loaded: (state): boolean => state._loaded.value,
    loading: (state): boolean => state._loading.value,
    mayLoadParameters: (state): boolean => {
      return !(state._loaded.value || state._loaded.loading)
    },
    // Various checks used throughout the app
    canSpecifyModelSettings: (state, getters): boolean => {
      return !!getters.zone && (state.regions.use ? !!getters.region : true)
    },
    // These are the 'current' of the various modules
    gridModel: (state): Optional<string> => {
      const id = state.gridModels.current
      if (id) {
        const gridModel = state.gridModels.available[`${id}`]
        return gridModel
          ? gridModel.name
          : null
      } else {
        return null
      }
    },
    zone: (state): Optional<Zone> => {
      return state.zones.current ? state.zones.available[`${state.zones.current}`] : null
    },
    region: (state, getters): Optional<Region> => {
      return state.regions.use && getters.zone ? getters.zone._regions[`${state.regions.current}`] : null
    },
    facies: (state, getters): Optional<Facies> => {
      return getters['facies/byId'](state.facies.global.current)
    },
    truncationRule: (state, getters): Optional<TruncationRule> => {
      // FIXME: This only works if there is one and ONLY one truncation rule in existence for a given zone/region
      //   use truncationRules.current in stead
      return getters['truncationRules/current']
    },
    regionParameter: (state): Optional<string> => {
      return state.parameters.region.selected
    },
    blockedWellParameter: (state): Optional<string> => {
      return state.parameters.blockedWell.selected
    },
    blockedWellLogParameter: (state): Optional<string> => {
      return state.parameters.blockedWellLog.selected
    },
    gridModels: (state, getters): string[] => {
      return getters['gridModels/names']
    },
    allFields: (state): GaussianRandomField[] => {
      return Object.values(state.gaussianRandomFields.available)
    },
    fields: (state, getters): GaussianRandomField[] => {
      return sortAlphabetically(
        Object.values(state.gaussianRandomFields.available)
          .filter((field): boolean => hasCurrentParents(field, getters))
      )
    },
    field: (state): (id: ID) => Optional<GaussianRandomField> => (id: ID): Optional<GaussianRandomField> => {
      return state.gaussianRandomFields.available[`${id}`] || null
    },
    // These are the 'available' for various modules / properties
    zones: (state): Zone[] => {
      return Object.values(state.zones.available)
    },
    regions: (state, getters): Region[] => {
      return getters.zone ? getters.zone.regions : []
    },
    faciesTable: (state): GlobalFacies[] => {
      return Object.values(state.facies.global.available)
        .sort((a, b): number => a.code - b.code)
    },
    fmuMode: (state, getters): boolean => getters.fmuUpdatable && !state.fmu.onlyUpdateFromFmu.value,
    fmuUpdatable: (state): boolean => state.fmu.runFmuWorkflows.value || state.fmu.onlyUpdateFromFmu.value,
    // User options
    options: (state): object => {
      return Object.keys(state.options)
        .reduce((obj, key): object => {
          obj[`${key}`] = state.options[`${key}`].value
          return obj
        }, {})
    },
    // ...
    simulationSettings: (state, getters): ({ field, zone }: { field?: GaussianRandomField, zone?: Zone}) => SimulationSettings => ({ field = undefined, zone = undefined }: { field?: GaussianRandomField, zone?: Zone } = { zone: undefined, field: undefined }): SimulationSettings => {
      const grid = state.parameters.grid
      const fieldSettings = field
        ? field.settings
        : {
          gridModel: null,
        }
      zone = zone || getters.zone
      const globalSettings = grid && !grid._waiting
        ? {
          gridAzimuth: grid.azimuth,
          gridSize: {
            // TODO: Get Z (thickness) based on the zone name
            ...(
              fieldSettings.gridModel && fieldSettings.gridModel.use
                ? fieldSettings.gridModel.size
                : grid.size
            ),
          },
          simulationBox: {
            // TODO: Get Z (thickness) based on the zone name
            // TODO: Add quality
            ...grid.simBox.size,
            z: zone
              // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
              // @ts-ignore
              ? grid.simBox.size.z instanceof Object
                ? grid.simBox.size.z[zone.code]
                : grid.simBox.size.z // Assuming it is a number
              : 0,
          },
          simulationBoxOrigin: {
            ...grid.simBox.origin,
          },
        }
        : defaultSimulationSettings()
      return {
        ...globalSettings,
        ...fieldSettings,
      }
    },
    // Utility method for getting IDs
    id: (state): (type: string, name: string) => Optional<ID> => (type: string, name: string): Optional<ID> => {
      const mapping = {
        gaussianRandomField: 'gaussianRandomFields.available',
        facies: 'facies.global.available',
      }
      const items = resolve(mapping[`${type}`], state)
      if (items) {
        const item = Object.values(items).find((item): boolean => item.name === name)
        if (item) {
          return item.id
        }
      }
      return null
    },
    byId: (state): <T extends BaseItem>(id: ID) => Optional<T> => <T extends BaseItem>(id: ID): Optional<T> => {
      const relevant = Object.values(state)
        .map((thing): Identified<T> => thing.available)
        .filter((items): boolean => items && hasOwnProperty(items, id))
      return relevant.length > 0
        ? relevant[0][`${id}`]
        : null
    }
  },
})

const initialState = JSON.stringify(store.state)

export default store

export function resetState (): void {
  store.commit('RESET', JSON.parse(initialState))
}

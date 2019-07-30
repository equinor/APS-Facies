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

import { RootState } from '@/store/typing'
import { ID } from '@/utils/domain/types'
import { Optional } from '@/utils/typing'
import { Identified, SimulationSettings } from '@/utils/domain/bases/interfaces'

import Zone, { Region } from '@/utils/domain/zone'
import { GaussianRandomField, TruncationRule } from '@/utils/domain'
import GlobalFacies from '@/utils/domain/facies/global'
import Facies from '@/utils/domain/facies/local'
import BaseItem from '@/utils/domain/bases/baseItem'

import {
  defaultSimulationSettings,
  getParameters,
  hasCurrentParents,
  resolve,
  sortAlphabetically,
} from '@/utils'

Vue.use(Vuex)

const store: Store<RootState> = new Vuex.Store({
  // @ts-ignore
  state: {
    _loaded: false,
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
    gaussianRandomFields,
    truncationRules,
    parameters,
    constants,
    options,
    modelFileLoader,
    modelFileExporter,
  },

  actions: {
    async fetch ({ dispatch, commit, state }): Promise<void> {
      if (!state._loaded) {
        await Promise.all([
          dispatch('gridModels/fetch'),
          dispatch('constants/fetch'),
          dispatch('truncationRules/fetch'),
          dispatch('parameters/path/fetch'),
          dispatch('parameters/names/workflow/fetch'),
          dispatch('parameters/names/project/fetch'),
        ])
        commit('FINISHED')
      }
    },
    async populate ({ dispatch, commit }, data): Promise<void> {
      commit('LOADING', { loading: true, message: 'Loading job. Please wait.' })
      try {
        await dispatch('fetch')

        // Grid model
        await dispatch('gridModels/select', data.gridModels.current)

        // Parameters
        for (const parameter of getParameters(data.parameters)) {
          // @ts-ignore
          const { selected } = resolve(parameter, data.parameters)
          if (selected) {
            await dispatch(`parameters/${parameter.replace('.', '/')}/select`, selected)
          } else if (parameter === 'grid') {
            await dispatch('parameters/grid/populate', data.parameters.grid)
            await dispatch('parameters/grid/simBox/populate', data.parameters.grid.simBox)
          } else {
            // Ignored
          }
        }

        // Zones
        await dispatch('zones/populate', { zones: Object.values(data.zones.available) })
        await dispatch('zones/current', { id: data.zones.current })

        // Regions
        await dispatch('regions/use', { use: data.regions.use, fetch: false })
        await dispatch('regions/current', { id: data.regions.current })

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
      } finally {
        commit('LOADING', { loading: false })
      }
    },
  },

  mutations: {
    RESET: (state, initial): void => {
      Object.assign(state, initial)
    },
    FINISHED: (state): void => {
      state._loaded = true
    },
    LOADING: (state, { loading, message = '' }): void => {
      state._loading.value = loading
      state._loading.message = message
    }
  },

  getters: {
    // Various checks used throughout the app
    canSpecifyModelSettings: (state, getters): boolean => {
      return !!getters.zone && (state.regions.use ? !!getters.region : true)
    },
    // These are the 'current' of the various modules
    gridModel: (state): Optional<string> => {
      return state.gridModels.current
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
    },
    // User options
    options: (state): object => {
      return Object.keys(state.options)
        .reduce((obj, key): object => {
          obj[`${key}`] = state.options[`${key}`].value
          return obj
        }, {})
    },
    // ...
    simulationSettings: (state, getters): (field: GaussianRandomField) => SimulationSettings => (field: GaussianRandomField): SimulationSettings => {
      const grid = state.parameters.grid
      const fieldSettings = field
        ? field.settings
        : {
          gridModel: null,
        }
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
            z: getters.zone
              // @ts-ignore
              ? grid.simBox.size.z instanceof Object
                ? grid.simBox.size.z[getters.zone.code]
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
        'gaussianRandomField': 'gaussianRandomFields.available',
        'facies': 'facies.global.available',
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
    byId: (state) => (id: ID) => {
      const relevant = Object.values(state)
        .map((thing): Identified<BaseItem> => thing.available)
        .filter((items): boolean => items && items.hasOwnProperty(id))
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

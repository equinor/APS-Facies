import Vue from 'vue'
import Vuex from 'vuex'

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
import modelName from '@/store/modules/modelName'
import workflowName from '@/store/modules/workflowName'

import { mirrorZoneRegions } from '@/store/utils'
import { defaultSimulationSettings, hasCurrentParents, resolve } from '@/utils'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
  },

  strict: process.env.NODE_ENV !== 'production',

  plugins: [
    mirrorZoneRegions,
  ],

  modules: {
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
    modelName,
    workflowName
  },

  actions: {
    fetch ({ dispatch }) {
      dispatch('gridModels/fetch')
      dispatch('constants/fetch')
      dispatch('truncationRules/fetch')
      dispatch('parameters/path/fetch')
    },
  },

  mutations: {
  },

  getters: {
    // Various checks used throughout the app
    canSpecifyModelSettings: (state, getters) => {
      return !!getters.zone && (state.regions.use ? !!getters.region : true)
    },
    // These are the 'current' of the various modules
    gridModel: (state) => {
      return state.gridModels.current
    },
    zone: (state) => {
      return state.zones.current ? state.zones.available[`${state.zones.current}`] : null
    },
    region: (state) => {
      return state.regions.use ? state.regions.available[`${state.regions.current}`] : null
    },
    facies: (state) => {
      return state.facies.current
    },
    truncationRule: (state, getters) => {
      // FIXME: This only works if there is one and ONLY one truncation rule in existence for a given zone/region
      //   use truncationRules.current in stead
      return getters['truncationRules/current']
    },
    regionParameter: (state) => {
      return state.parameters.region.selected
    },
    blockedWellParameter: (state) => {
      return state.parameters.blockedWell.selected
    },
    blockedWellLogParameter: (state) => {
      return state.parameters.blockedWellLog.selected
    },
    allFields: (state) => {
      return Object.values(state.gaussianRandomFields.fields)
    },
    fields: (state, getters) => {
      return Object.values(state.gaussianRandomFields.fields)
        .filter(field => hasCurrentParents(field, getters))
    },
    field: (state) => (id) => {
      return state.gaussianRandomFields.fields[`${id}`]
    },
    // These are the 'available' for various modules / properties
    zones: (state) => {
      return state.zones.available
    },
    regions: (state) => {
      return state.regions.available
    },
    faciesTable: (state) => {
      return Object.values(state.facies.global.available)
    },
    // User options
    options: (state) => {
      return Object.keys(state.options)
        .reduce((obj, key) => {
          obj[key] = state.options[key].value
          return obj
        }, {})
    },
    // ...
    simulationSettings: (state, getters) => (grfId) => {
      const grid = state.parameters.grid
      const fieldSettings = grfId
        ? state.gaussianRandomFields.fields[`${grfId}`].settings
        : {}
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
              ? grid.simBox.size.z[getters.zone.code]
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
    id: (state) => (type, name) => {
      const mapping = {
        'gaussianRandomField': 'gaussianRandomFields.fields',
        'facies': 'facies.global.available',
      }
      const items = resolve(mapping[`${type}`], state)
      if (items) {
        const item = Object.values(items).find(item => item.name === name)
        if (item) {
          return item.id
        }
      }
      return null
    },
    byId: (state) => (id) => {
      const relevant = Object.values(state)
        .map(thing => thing.available || thing.field)
        .filter(items => !!items && items.hasOwnProperty(id))
      return relevant.length > 0
        ? relevant[0][`${id}`]
        : null
    }
  },
})

import Vue from 'vue'
import Vuex from 'vuex'

import copyPaste from '@/store/modules/copyPaste'
import message from '@/store/modules/message'
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

import {
  defaultSimulationSettings,
  getParameters,
  hasCurrentParents,
  resolve,
  sortAlphabetically,
} from '@/utils'

Vue.use(Vuex)

const store = new Vuex.Store({
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
    async fetch ({ dispatch, commit, state }) {
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
    async populate ({ dispatch, commit }, data) {
      commit('LOADING', { loading: true, message: 'Loading job. Please wait.' })
      try {
        await dispatch('fetch')

        // Grid model
        await dispatch('gridModels/select', data.gridModels.current)

        // Parameters
        for (const parameter of getParameters(data.parameters)) {
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
        await dispatch('gaussianRandomFields/populate', Object.values(data.gaussianRandomFields.fields))

        // Truncation rules
        await dispatch('truncationRules/populate', data.truncationRules)
      } finally {
        commit('LOADING', { loading: false })
      }
    },
  },

  mutations: {
    RESET: (state, initial) => {
      Object.assign(state, initial)
    },
    FINISHED: state => {
      state._loaded = true
    },
    LOADING: (state, { loading, message = '' }) => {
      state._loading.value = loading
      state._loading.message = message
    }
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
    region: (state, getters) => {
      return state.regions.use && getters.zone ? getters.zone._regions[`${state.regions.current}`] : null
    },
    facies: (state, getters) => {
      return getters['facies/byId'](state.facies.global.current)
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
      return sortAlphabetically(
        Object.values(state.gaussianRandomFields.fields)
          .filter(field => hasCurrentParents(field, getters))
      )
    },
    field: (state) => (id) => {
      return state.gaussianRandomFields.fields[`${id}`]
    },
    // These are the 'available' for various modules / properties
    zones: (state) => {
      return Object.values(state.zones.available)
    },
    regions: (state, getters) => {
      return getters.zone ? getters.zone.regions : []
    },
    faciesTable: (state) => {
      return Object.values(state.facies.global.available)
    },
    // User options
    options: (state) => {
      return Object.keys(state.options)
        .reduce((obj, key) => {
          obj[`${key}`] = state.options[`${key}`].value
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

const initialState = JSON.stringify(store.state)

export default store

export function resetState () {
  store.commit('RESET', JSON.parse(initialState))
}

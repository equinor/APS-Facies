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
import { mirrorZoneRegions } from '@/store/utils'
import { hasCurrentParents, resolve } from '@/utils'
import modelFileLoader from '@/store/modules/modelFileLoader'

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
  },

  actions: {
    fetch ({ dispatch }) {
      dispatch('gridModels/fetch')
      dispatch('constants/fetch')
      dispatch('truncationRules/fetch')
    },
  },

  mutations: {
  },

  getters: {
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
      return state.truncationRules.rules ? Object.values(state.truncationRules.rules).find(rule => hasCurrentParents(rule, getters)) : null
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
    fields: (state, getters) => {
      // const fields = state.gaussianRandomFields.fields
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
      return Object.values(state.facies.available).map(facies => { return { id: facies.id, name: facies.name, code: facies.code, color: facies.color } })
    },
    // Utility method for getting IDs
    id: (state) => (type, name) => {
      const mapping = {
        'gaussianRandomField': 'gaussianRandomFields.fields',
        'facies': 'facies.available',
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
  },
})

import Vue from 'vue'
import Vuex from 'vuex'
import gridModels from '@/store/modules/gridModels'
import zones from '@/store/modules/zones'
import regions from '@/store/modules/regions'
import facies from '@/store/modules/facies'
import gaussianRandomFields from '@/store/modules/gaussianRandomFields'
import parameters from '@/store/modules/parameters'
import constants from '@/store/modules/constants'
import { mirrorZoneRegions } from '@/store/utils'

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
    parameters,
    constants,
  },

  actions: {
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
    zoneParameter: (state) => {
      return state.parameters.zone.selected
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
  },
})

import Vue from 'vue'
import Vuex from 'vuex'
import gridModels from 'Store/modules/gridModels'
import zones from 'Store/modules/zones'
import facies from 'Store/modules/facies'
import gaussianRandomFields from 'Store/modules/gaussianRandomFields'
import parameters from 'Store/modules/parameters'
import constants from 'Store/modules/constants'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
  },

  strict: process.env.NODE_ENV !== 'production',

  modules: {
    gridModels,
    zones,
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
      return state.zones.available[`${state.zones.current}`]
    },
    region: (state, getters) => {
      // return getters.zone ? getters.zone.regions.current : null
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
    }
  },
})

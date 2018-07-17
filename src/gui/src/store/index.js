import Vue from 'vue'
import Vuex from 'vuex'
import gridModels from '@/store/modules/gridModels'
import zones from '@/store/modules/zones'
import regions from '@/store/modules/regions'
import facies from '@/store/modules/facies'
import parameters from '@/store/modules/parameters'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
  },

  strict: process.env.NODE_ENV !== 'production',

  modules: {
    gridModels,
    zones,
    regions,
    facies,
    parameters,
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
      return state.zones.current
    },
    region: (state) => {
      return state.regions.current
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
    }
  },
})

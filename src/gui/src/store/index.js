import Vue from 'vue'
import Vuex from 'vuex'
import rms from '@/api/rms'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    availableGridModels: [],
    availableZones: rms.zones,
    availableFacies: rms.facies,
    selectedGridModel: null,
    selectedZones: [],
    selectedRegions: [],
    currentZone: null,
    currentRegion: null,
    currentFacies: null,
  },

  strict: process.env.NODE_ENV !== 'production',

  getters: {
    availableGridModelNames: (state) => {
      return state.availableGridModels
    },
  },

  methods: {
    promiseSimpleCommit (commit, commitment, data, check = true, error = '') {
      return new Promise((resolve, reject) => {
        if (check) {
          commit(commitment, data)
          resolve(data)
        } else {
          reject(error)
        }
      })
    }
  },

  actions: {
    selectGridModel: ({getters, commit}, {selectedGridModel}) => {
      return new Promise((resolve, reject) => {
        if (getters.availableGridModelNames.includes(selectedGridModel)) {
          commit('gridModel', selectedGridModel)
          resolve(selectedGridModel)
        } else {
          reject(new Error('Selected grid model must be valid.'))
        }
      })
    },
    selectZones: ({commit, promiseSimpleCommit}, zones) => {
      return promiseSimpleCommit(commit, 'selectedZones', zones)
    },
    selectRegions: ({commit, promiseSimpleCommit}, regions) => {
      return promiseSimpleCommit(commit, 'selectedRegions', regions)
    },
    currentZone: ({commit, promiseSimpleCommit}, zone) => {
      return promiseSimpleCommit(commit, 'currentZone', zone)
    },
    currentRegion: ({commit, promiseSimpleCommit}, region) => {
      return promiseSimpleCommit(commit, 'currentRegion', region)
    },
    currentFacies: ({commit, promiseSimpleCommit}, facies) => {
      return promiseSimpleCommit(commit, 'currentFacies', facies)
    },
    fetchGridModels: ({commit}) => {
      rms.gridModels.then(result => {
        commit('availableGridModels', result)
      })
    }
  },

  mutations: {
    gridModel: (state, selectedGridModel) => {
      state.selectedGridModel = selectedGridModel
    },
    availableGridModels: (state, gridModels) => {
      state.availableGridModels = gridModels
    },
    selectedZones: (state, selectedZones) => {
      state.selectedZones = selectedZones
    },
    selectedRegions: (state, selectedRegions) => {
      state.selectedRegions = selectedRegions
    },
    currentZone: (state, currentZone) => {
      state.currentZone = currentZone
    },
    currentRegion: (state, currentRegion) => {
      state.currentRegion = currentRegion
    },
    currentFacies: (state, currentFacies) => {
      state.currentFacies = currentFacies
    }
  },
})

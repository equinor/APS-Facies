import Vue from 'vue'
import Vuex from 'vuex'
import rms from '@/api/rms'
import { promiseSimpleCommit, compareFacies, indexOfFacies } from '@/store/utils'

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
    selectZones: ({commit}, zones) => {
      return promiseSimpleCommit(commit, 'selectedZones', zones)
    },
    selectRegions: ({commit}, regions) => {
      return promiseSimpleCommit(commit, 'selectedRegions', regions)
    },
    currentZone: ({commit}, zone) => {
      return promiseSimpleCommit(commit, 'currentZone', zone)
    },
    currentRegion: ({commit}, region) => {
      return promiseSimpleCommit(commit, 'currentRegion', region)
    },
    currentFacies: ({commit}, facies) => {
      return promiseSimpleCommit(commit, 'currentFacies', facies)
    },
    removeSelectedFacies: ({commit, state}) => {
      const selectedFacies = state.currentFacies
      const faciesIndex = state.availableFacies.findIndex(facies => compareFacies(selectedFacies, facies))
      if (faciesIndex >= 0) {
        commit('removeFacies', faciesIndex)
      }
    },
    faciesChanged: ({commit, state}, facies) => {
      let faciesIndex = indexOfFacies(state, facies)
      if (faciesIndex >= 0) {
        commit('replaceFacies', {index: faciesIndex, facies})
      } else {
        commit('addFacies', facies)
        faciesIndex = indexOfFacies(state, facies)
      }
      return faciesIndex
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
    },
    replaceFacies: (state, {index, facies}) => {
      state.availableFacies[index] = facies
    },
    addFacies: (state, facies) => {
      state.availableFacies.push(facies)
    },
    removeFacies: (state, index) => {
      state.availableFacies.splice(index, 1)
    },
  },
})

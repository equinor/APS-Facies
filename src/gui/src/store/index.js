import Vue from 'vue'
import Vuex from 'vuex'
import rms from '@/api/rms'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    availableGridModels: rms.gridModels,
    availableZones: rms.zones,
    availableFacies: rms.facies,
    selectedGridModel: null,
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
    }
  },

  mutations: {
    gridModel: (state, selectedGridModel) => {
      state.selectedGridModel = selectedGridModel
    },
  },
})

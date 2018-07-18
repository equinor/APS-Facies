import rms from 'Api/rms'
import { promiseSimpleCommit, compareFacies, indexOfFacies } from 'Store/utils'

export default {
  namespaced: true,

  state: {
    available: [],
    current: null,
  },

  modules: {},

  actions: {
    current: ({commit}, facies) => {
      return promiseSimpleCommit(commit, 'CURRENT', facies)
    },
    removeSelectedFacies: ({commit, state}) => {
      const selectedFacies = state.current
      const faciesIndex = state.available.findIndex(facies => compareFacies(selectedFacies, facies))
      if (faciesIndex >= 0) {
        commit('REMOVE', faciesIndex)
      }
    },
    changed: ({commit, state}, facies) => {
      let faciesIndex = indexOfFacies(state, facies)
      if (faciesIndex >= 0) {
        commit('REPLACE', {index: faciesIndex, facies})
      } else {
        commit('ADD', facies)
        faciesIndex = indexOfFacies(state, facies)
      }
      return faciesIndex
    },
    fetch: ({commit, rootGetters}) => {
      return rms.facies(rootGetters.gridModel, rootGetters.blockedWellParameter, rootGetters.blockedWellLogParameter)
        .then(facies => {
          // TODO: Add colors
          commit('AVAILABLE', facies)
        })
    },
  },

  mutations: {
    AVAILABLE: (state, facies) => {
      state.available = facies
    },
    CURRENT: (state, currentFacies) => {
      state.current = currentFacies
    },
    REPLACE: (state, {index, facies}) => {
      state.available[`${index}`] = facies
    },
    ADD: (state, facies) => {
      state.available.push(facies)
    },
    REMOVE: (state, index) => {
      state.available.splice(index, 1)
    },
  },

  getters: {},
}

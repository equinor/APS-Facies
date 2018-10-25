import { fetchParameterHelper } from '@/store/utils'
import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: ({ state, commit, dispatch }, regionParameter) => {
      return new Promise((resolve, reject) => {
        if (state.available.includes(regionParameter)) {
          commit('CURRENT', regionParameter)
          dispatch('regions/use', { use: !!regionParameter }, { root: true })
            .then(() => {
              resolve(regionParameter)
            })
            .catch(error => {
              reject(error)
            })
        } else {
          let errorMsg = `Selected regionParam ( ${regionParameter} ) is not present int the current project\n\n`
          errorMsg += `Tip: RegionParamName in the APS model File must be one of { ${state.available.join()} } `
          reject(new Error(errorMsg))
        }
      })
    },
    fetch: ({ commit, dispatch, rootGetters }) => {
      commit('CURRENT', null)
      return fetchParameterHelper(commit, dispatch, rms.regionParameters(rootGetters.gridModel))
    },
  },

  mutations: {
    AVAILABLE: (state, regionParameters) => {
      state.available = regionParameters
    },
    CURRENT: (state, regionParameter) => {
      state.selected = regionParameter
    },
  },

  getters: {},
}

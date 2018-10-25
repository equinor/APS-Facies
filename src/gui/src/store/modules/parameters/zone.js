import { promiseSimpleCommit, fetchParameterHelper } from '@/store/utils'
import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: ({ state, commit, dispatch }, zoneParameter) => {
      return new Promise((resolve, reject) => {
        if (state.available.includes(zoneParameter)) {
          return promiseSimpleCommit(commit, 'CURRENT', zoneParameter)
            .then(() =>
              dispatch('zones/fetch', null, { root: true })
                .then(() => resolve(zoneParameter))
            )
        } else {
          let errorMsg = `Selected zoneParam ( ${zoneParameter} ) is not present int the current project\n\n`
          errorMsg += `Tip: zoneParamName in the APS model File must be one of { ${state.available.join()} } `
          reject(new Error(errorMsg))
        }
      })
    },
    fetch: ({ commit, dispatch, rootGetters }) => {
      return fetchParameterHelper(commit, dispatch, rms.zoneParameters(rootGetters.gridModel))
    },
  },

  mutations: {
    AVAILABLE: (state, zoneParameters) => {
      state.available = zoneParameters
    },
    CURRENT: (state, zoneParameter) => {
      state.selected = zoneParameter
    },
  },

  getters: {},
}

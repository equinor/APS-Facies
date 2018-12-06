import rms from '@/api/rms'
import { isEmpty, makeData } from '@/utils'
import { GlobalFacies } from '@/store/utils/domain'
import Vue from 'vue'
import { promiseSimpleCommit, changeFacies } from '@/store/utils'

export default {
  namespaced: true,

  state: {
    available: {},
    current: null,
  },

  modules: {},

  actions: {
    fetch: ({ dispatch, rootGetters }) => {
      return rms.facies(rootGetters.gridModel, rootGetters.blockedWellParameter, rootGetters.blockedWellLogParameter)
        .then(facies => dispatch('populate', facies))
    },
    populate: ({ commit, rootState }, facies) => {
      // TODO: Add colors (properly)
      for (let i = 0; i < facies.length; i++) {
        const colors = rootState.constants.faciesColors.available
        facies[`${i}`].color = colors[`${i % colors.length}`]
      }
      const data = makeData(facies, GlobalFacies)
      commit('AVAILABLE', data)
    },
    new: ({ dispatch, state, rootState }, { code, name, color }) => {
      return new Promise((resolve, reject) => {
        if (isEmpty(code) || code < 0) {
          // TODO: Find the highest values in the Global Facies Table (from rms, as some may have been deleted)
          code = 1 + Object.values(state.available)
            .map(facies => facies.code)
            .reduce((a, b) => Math.max(a, b), 0)
        }
        if (isEmpty(name)) {
          name = `F${code}`
        }
        if (isEmpty(color)) {
          const colors = rootState.constants.faciesColors.available
          color = colors[code % colors.length]
        }
        const facies = new GlobalFacies({ code, name, color })
        dispatch('changed', facies)
        resolve(facies)
      })
    },
    current: ({ commit }, { id }) => {
      return promiseSimpleCommit(commit, 'CURRENT', { id })
    },
    changed: (context, facies) => changeFacies(context, facies),
  },

  mutations: {
    AVAILABLE: (state, facies) => {
      Vue.set(state, 'available', facies)
    },
    CURRENT: (state, { id }) => {
      state.current = id
    },
    UPDATE: (state, facies) => {
      Vue.set(state.available, facies.id, facies)
    },
  },

  getters: {
    selected: (state, getters, rootState, rootGetters) => {
      return rootGetters['facies/selected']
        .map(({ facies }) => state.available[`${facies}`])
    }
  },
}

import rms from '@/api/rms'
import { isEmpty, makeData } from '@/utils'
import { GlobalFacies } from '@/utils/domain'
import Vue from 'vue'
import { APSTypeError } from '@/utils/domain/errors'

function getColor ({ rootState }, code) {
  const colors = rootState.constants.faciesColors.available
  return colors[`${code % colors.length}`]
}

async function getFaciesFromRMS ({ rootGetters }) {
  const facies = await rms.facies(rootGetters.gridModel, rootGetters.blockedWellParameter, rootGetters.blockedWellLogParameter)
  return facies
}

function findExisting (items, { code, name }) {
  items = Array.isArray(items) ? items : Object.values(items)
  return items
    .find(facies => facies.code === code || facies.name === name)
}

export default {
  namespaced: true,

  state: {
    available: {},
    current: null,
    _loading: false,
    _inRms: [],
  },

  modules: {},

  actions: {
    fetch: async ({ commit, dispatch, rootGetters }) => {
      commit('LOADING', true)
      const facies = await getFaciesFromRMS({ rootGetters })
      commit('LOADING', false)
      await dispatch('populate', facies)
      commit('IN_RMS', facies)
    },
    populate: ({ commit, state, rootState }, facies) => {
      const minFaciesCode = facies.map(({ code }) => code).reduce((min, curr) => min < curr ? min : curr, Number.POSITIVE_INFINITY)
      facies.forEach(facies => {
        if (!facies.color) {
          facies.color = getColor({ rootState }, facies.code - minFaciesCode)
        }
      })
      const data = makeData(facies, GlobalFacies, state.available)
      commit('AVAILABLE', data)
    },
    new: ({ commit, state, rootState }, { code, name, color }) => {
      if (isEmpty(code) || code < 0) {
        code = 1 + Object.values(state.available)
          .concat(state._inRms)
          .map(facies => facies.code)
          .reduce((a, b) => Math.max(a, b), 0)
      }
      if (isEmpty(name)) {
        name = `F${code}`
      }
      if (isEmpty(color)) {
        color = getColor({ rootState }, code)
      }
      if (findExisting(state._inRms, { code, name })) {
        throw new APSTypeError(`There already exists a facies with code = ${code}, or name = ${name} in RMS`)
      }
      const facies = new GlobalFacies({ code, name, color })
      commit('ADD', facies)
      return facies
    },
    current: ({ commit }, { id }) => {
      commit('CURRENT', { id })
    },
    removeSelectedFacies: async ({ commit, dispatch, state }) => {
      if (state.current) {
        commit('REMOVE', { id: state.current })
        await dispatch('current', { id: null })
      }
    },
    changeColor: ({ commit }, { id, color }) => {
      commit('CHANGE', { id, name: 'color', value: color })
    },
    changeName: ({ commit }, { id, name }) => {
      commit('CHANGE', { id, name: 'name', value: name })
    },
    changeAlias: ({ commit }, { id, alias }) => {
      commit('CHANGE', { id, name: 'alias', value: alias })
    },
  },

  mutations: {
    AVAILABLE: (state, facies) => {
      Vue.set(state, 'available', facies)
    },
    CURRENT: (state, { id }) => {
      state.current = id
    },
    LOADING: (state, toggle) => {
      Vue.set(state, '_loading', toggle)
    },
    ADD: (state, facies) => {
      Vue.set(state.available, facies.id, facies)
    },
    REMOVE: (state, { id }) => {
      Vue.delete(state.available, id)
    },
    CHANGE: (state, { id, name, value }) => {
      Vue.set(state.available[`${id}`], name, value)
    },
    IN_RMS: (state, facies) => {
      Vue.set(state, '_inRms', facies)
    },
  },

  getters: {
    selected: (state, getters, rootState, rootGetters) => {
      return rootGetters['facies/selected']
        .map(({ facies }) => state.available[`${facies.id}`])
    }
  },
}

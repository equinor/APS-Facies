import Vue from 'vue'
import { cloneDeep } from 'lodash'

import { AVAILABLE } from '@/store/mutations'

import { FaciesGroup } from '@/store/utils/domain/facies'
import { getId } from '@/utils/typing'
import { toIdentifiedObject } from '@/utils'

export default {
  namespaced: true,

  state: {
    available: {},
  },

  modules: {},

  actions: {
    populate ({ commit, rootGetters }, groups) {
      groups = groups.map(group => new FaciesGroup(group))
      groups.forEach(group => {
        if (group.facies.some(facies => !rootGetters['facies/byId'](facies))) {
          throw new Error(`The group reference a facies that does not exist`)
        }
      })
      commit('AVAILABLE', toIdentifiedObject(groups))
    },
    async get ({ getters, dispatch }, { facies, parent }) {
      let group = getters.byFacies(facies, parent)
      if (!group) {
        group = await dispatch('add', { facies, ...parent })
      }
      return group
    },
    add ({ commit, state, getters }, { facies, zone, region = null }) {
      // TODO: Deal with missing parents
      // TODO: ensure that none of the given facies are used
      if (facies.some(facies => getters.used(facies))) {
        throw new Error(`The facies, ${facies}, has already been specified`)
      }
      const group = new FaciesGroup({ facies, zone, region })
      const groups = cloneDeep(state.available)
      groups[getId(group)] = group
      commit('AVAILABLE', groups)
      return group
    },
    remove ({ commit, state }, group) {
      const groups = cloneDeep(state.available)
      delete groups[getId(group)]
      commit('AVAILABLE', groups)
    },
    update ({ commit }, { group, facies }) {
      commit('UPDATE', { group, facies })
    }
  },

  mutations: {
    AVAILABLE,
    UPDATE: (state, { group, facies }) => {
      Vue.set(state.available[`${group.id}`], '_facies', facies)
    },
  },

  getters: {
    byFacies: (state) => (facies, parent) => {
      return Object.values(state.available).find(group => group.isChildOf(parent) && group.contains(facies))
    },
    used: (state) => facies => {
      const used = new Set()
      Object.values(state.available)
        .forEach(group => {
          group.facies.forEach(facies => {
            used.add(getId(facies))
          })
        })
      return used.has(getId(facies))
    },
    text: (state, getters, rootState, rootGetters) => group => {
      return group.facies
        .map(facies => rootGetters['facies/name'](facies))
        .reduce((text, name) => text ? `${text}, ${name}` : name, '')
    }
  },
}

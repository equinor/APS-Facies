import Vue from 'vue'

import templates from '@/store/templates/truncationRules'
import { addItem } from '@/store/actions'

const isEqual = (values, others) => {
  values = Object.values(values)
  others = Object.values(others)
  return values.length === others.length && values.every(value => others.indexOf(({ name, type }) => value.name === name && type === value.type))
}

export default {
  namespaced: true,

  state: {
    available: {},
  },

  actions: {
    fetch ({ dispatch, state }) {
      const promises = []
      templates.types.forEach(rule => {
        if (Object.values(state.available).indexOf(({ name, type }) => rule.name === name && rule.type === type) < 0) {
          promises.push(dispatch('add', rule))
        }
      })
      return Promise.all(promises)
    },
    populate ({ commit }, types) {
      if (isEqual(templates.types, types)) {
        return new Promise((resolve) => {
          commit('AVAILABLE', types)
          resolve(Object.keys(types))
        })
      } else {
        throw new Error('NOT IMPLEMENTED: The given types to not match the types given in the templates')
      }
    },
    add ({ commit }, rule) {
      return addItem({ commit }, { item: rule })
    }
  },

  mutations: {
    ADD (state, { id, item }) {
      Vue.set(state.available, id, item)
    },
    AVAILABLE (state, types) {
      Vue.set(state, 'available', types)
    }
  },
}

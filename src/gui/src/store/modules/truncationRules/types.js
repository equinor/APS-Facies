import Vue from 'vue'

import templates from '@/store/templates/truncationRules'
import { addItem } from '@/store/actions'
import { identify } from '@/utils/helpers'

const isEqual = (values, others) => {
  values = Object.values(values)
  others = Object.values(others)
  return values.length === others.length
    && values.every(value => others.indexOf(({ name, type }) => value.name === name && type === value.type))
}

export default {
  namespaced: true,

  state: {
    available: {},
  },

  actions: {
    fetch ({ commit }) {
      const types = identify(templates.types)
      commit('AVAILABLE', types)
    },
    populate ({ commit }, types) {
      if (isEqual(templates.types, types)) {
        commit('AVAILABLE', types)
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

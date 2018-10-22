import Vue from 'vue'

import templates from '@/store/templates/truncationRules'
import { addItem } from '@/store/actions'

export default {
  namespaced: true,

  state: {
    available: {},
  },

  actions: {
    fetch ({ dispatch }) {
      templates.types.map(rule => dispatch('add', rule))
    },
    add ({ commit }, rule) { addItem({ commit }, { item: rule }) }
  },

  mutations: {
    ADD (state, { id, item }) {
      Vue.set(state.available, id, item)
    },
  },
}

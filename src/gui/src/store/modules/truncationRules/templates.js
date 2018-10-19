import templates from '@/store/templates/truncationRules'
import types from '@/store/modules/truncationRules/types'
import { addItem } from '@/store/actions'
import { ADD_ITEM } from '@/store/mutations'

export default {
  namespaced: true,

  state: {
    available: {},
  },

  modules: {
    types,
  },

  actions: {
    fetch ({ dispatch }) {
      dispatch('types/fetch')
      templates.templates.map(template => dispatch('add', template))
    },
    add ({ commit, state }, template) {
      template.type = Object.keys(state.types.available).find(id => state.types.available[`${id}`].type === template.type)
      addItem({ commit }, { item: template })
    }
  },

  mutations: {
    ADD: (state, { id, item }) => {
      ADD_ITEM(state.available, { id, item })
    },
  },
}

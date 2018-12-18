import Vue from 'vue'
import { cloneDeep } from 'lodash'

import templates from '@/store/templates/truncationRules'
import types from '@/store/modules/truncationRules/types'
import { addItem } from '@/store/actions'
import { ADD_ITEM } from '@/store/mutations'
import { isUUID } from '@/utils/typing'

const missingTemplates = (_templates, state) => {
  const name = template => {
    const type = isUUID(template.type) ? state.types.available[template.type].type : template.type
    return `${type}::${template.name}`
  }
  const names = Object.values(_templates).map(template => name(template))
  return templates.templates.filter((template) => names.indexOf(name(template)) === -1)
}

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
      return Promise.all([
        dispatch('types/fetch'),
        ...templates.templates.map(template => dispatch('add', template)),
      ])
    },
    async populate ({ commit, dispatch, state }, { available, types }) {
      await dispatch('types/populate', types.available)
      // TODO: Deal with there being other 'official' templates than those to be populated
      commit('AVAILABLE', available)
      const missing = missingTemplates(available, state)
      return Promise.all(missing.map(template => dispatch('add', template)))
    },
    add ({ commit, state }, template) {
      template = cloneDeep(template)
      template.type = Object.keys(state.types.available).find(id => state.types.available[`${id}`].type === template.type)
      return addItem({ commit }, { item: template })
    }
  },

  mutations: {
    ADD: (state, { id, item }) => {
      ADD_ITEM(state.available, { id, item })
    },
    AVAILABLE: (state, templates) => {
      Vue.set(state, 'available', templates)
    },
  },
}

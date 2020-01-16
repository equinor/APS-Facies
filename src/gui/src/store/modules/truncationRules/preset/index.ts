import Vue from 'vue'

import { Module } from 'vuex'

import { RootState } from '@/store/typing'
import PresetState from '@/store/modules/truncationRules/preset/typing'

import { notEmpty } from '@/utils'
import { hasOwnProperty } from '@/utils/helpers'

const state: Module<PresetState, RootState> = {
  namespaced: true,

  state: {
    type: '',
    template: '',
  },

  actions: {
    async fetch ({ dispatch, rootState, rootGetters }, rule = null): Promise<void> {
      rule = rule || rootGetters.truncationRule
      if (rule) {
        const type = Object.values(rootState.truncationRules.templates.types.available)
          .find(({ type }): boolean => type === rule.type)
        await dispatch('populate', {
          type: type ? type.id : null,
          template: rule.name,
        })
      } else {
        await dispatch('reset')
      }
    },

    populate ({ commit }, preset): void {
      if (preset.type) commit('CHANGE_TYPE', preset)
      if (preset.template) commit('CHANGE_TEMPLATE', preset)
    },

    async change ({ commit, dispatch, state, rootState, rootGetters }, { type, template }): Promise<void> {
      const current = rootGetters.truncationRule
      if (current && type !== state.type && template !== state.template) {
        await dispatch('truncationRules/remove', current.id, { root: true })
      }
      if (notEmpty(type)) {
        const types = rootState.truncationRules.templates.types.available
        const typeId = Object.keys(types).find((id): boolean => {
          const _type = types[`${id}`]
          return _type && _type.name === type
        })
        commit('CHANGE_TYPE', { type: typeId })
        commit('CHANGE_TEMPLATE', { template: null })
      }
      if (notEmpty(template)) {
        commit('CHANGE_TEMPLATE', { template })
        await dispatch('truncationRules/addRuleFromTemplate', undefined, { root: true })
      }
    },
    reset ({ commit }): void {
      commit('CHANGE_TYPE', { type: null })
      commit('CHANGE_TEMPLATE', { template: null })
    },
  },

  mutations: {
    CHANGE_TYPE: (state, { type }): void => {
      Vue.set(state, 'type', type)
    },
    CHANGE_TEMPLATE: (state, { template }): void => {
      if (template && hasOwnProperty(template, 'text')) {
        template = template.text
      }
      Vue.set(state, 'template', template)
    },
  }
}

export default state

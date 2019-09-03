import Vue from 'vue'

import templates from '@/store/templates/truncationRules.json'
import { addItem } from '@/store/actions'
import { identify } from '@/utils/helpers'

import { Module } from 'vuex'
import { TruncationRuleTemplate, TruncationRuleTemplateType, TruncationRuleTemplateState } from '@/store/modules/truncationRules/typing'
import { RootState } from '@/store/typing'
import { Identified } from '@/utils/domain/bases/interfaces'

function isEqual (values: TruncationRuleTemplateType[], others: Identified<TruncationRuleTemplate>): boolean {
  const _values = Object.values(values)
  const _others = Object.values(others)
  return _values.length === _others.length
    // @ts-ignore
    && _values.every((value): boolean => _others.indexOf(({ name, type }) => value.name === name && type === value.type))
}

const module: Module<TruncationRuleTemplateState, RootState> = {
  namespaced: true,

  state: {
    available: {},
  },

  actions: {
    fetch ({ commit }): void {
      const types = identify(templates.types)
      commit('AVAILABLE', types)
    },
    populate ({ commit }, types): void {
      // @ts-ignore
      if (isEqual(templates.types, types)) {
        commit('AVAILABLE', types)
      } else {
        throw new Error('NOT IMPLEMENTED: The given types to not match the types given in the templates')
      }
    },
    async add ({ commit }, rule): Promise<void> {
      await addItem({ commit }, { item: rule })
    }
  },

  mutations: {
    ADD (state, { id, item }): void {
      Vue.set(state.available, id, item)
    },
    AVAILABLE (state, types): void {
      Vue.set(state, 'available', types)
    }
  },
}

export default module

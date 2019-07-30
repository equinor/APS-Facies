import Vue from 'vue'

import { PanelsState } from '@/store/modules/panels/typing'
import APSTypeError from '@/utils/domain/errors/type'
import { Module } from 'vuex'
import { Context, RootState } from '@/store/typing'
import { isNumber } from 'lodash'

const PANELS = {
  'selection': ['zoneRegion', 'facies'],
  'preview': ['truncationRuleMap', 'truncationRuleRealization', 'gaussianRandomFields', 'crossPlots'],
  'settings': ['faciesProbability', 'truncationRule', 'gaussianRandomFields'],
}

function hasPanel (type: string, panel: string | undefined = undefined): boolean {
  if (Object.keys(PANELS).includes(type)) {
    return panel
      ? PANELS[`${type}`].includes(panel)
      : true
  } else {
    return false
  }
}

function getIndices (state: PanelsState, type: Section): number[] {
  return PANELS[type]
    .map((panel, index): [boolean, number] => [state[type][panel], index])
    .filter(([toggled, _]): boolean => toggled || isNumber(toggled))
    .map(([_, index]): number => index)
}

type Section = 'selection' | 'preview' | 'settings'

interface Specification<T=string> {
  type: Section
  panel: T
}

interface FullSpecification<T=string> extends Specification<T> {
  toggled: boolean
}

type Payload = Section | Specification<string | string[]>

function changePanel ({ commit }: Context<PanelsState, RootState>, payload: Payload, toggled: boolean | number): void {
  if (typeof payload === 'string') {
    if (hasPanel(payload)) {
      for (const panel of PANELS[`${payload}`]) {
        commit('CHANGE', { type: payload, panel, toggled })
      }
    } else {
      throw new APSTypeError(`'${payload}' is not a valid panel`)
    }
  } else if (Array.isArray(payload.panel)) {
    for (const panel of payload.panel) {
      commit('CHANGE', { type: payload.type, panel, toggled })
    }
  } else {
    commit('CHANGE', { ...payload, toggled })
  }
}

const module: Module<PanelsState, RootState> = {
  namespaced: true,

  state: {
    selection: {
      zoneRegion: false,
      facies: false,
    },
    preview: {
      truncationRuleMap: false,
      truncationRuleRealization: false,
      gaussianRandomFields: false,
      crossPlots: false,
    },
    settings: {
      faciesProbability: false,
      truncationRule: false,
      gaussianRandomFields: null,
    },
  },

  actions: {
    populate ({ commit }, panels: PanelsState): void {
      for (const type of Object.keys(panels)) {
        for (const panel of Object.keys(panels[`${type}`])) {
          commit('CHANGE', { type, panel, toggled: panels[`${type}`][`${panel}`] })
        }
      }
    },
    open (context, payload: Payload): void {
      changePanel(context, payload, true)
    },
    close (context, payload: Payload): void {
      changePanel(context, payload, false)
    },
    set (context, payload: FullSpecification): void {
      changePanel(context, payload, payload.toggled)
    },
    change (context, { type, indices }: { type: Section, indices: number[] }): void {
      if (!hasPanel(type)) throw new APSTypeError(`${type} is not a legal panel`)
      const panels = indices.map((index): boolean => PANELS[`${type}`][`${index}`])
      for (const panel of PANELS[`${type}`]) {
        changePanel(context, { type, panel }, panels.includes(panel))
      }
    },
  },

  mutations: {
    CHANGE (state, { type, panel, toggled }: FullSpecification): void {
      Vue.set(state[`${type}`], panel, toggled)
    }
  },

  getters: {
    selection (state): number[] { return getIndices(state, 'selection') },
    preview (state): number[] { return getIndices(state, 'preview') },
    settings (state): number[] { return getIndices(state, 'settings') },
  },
}

export default module

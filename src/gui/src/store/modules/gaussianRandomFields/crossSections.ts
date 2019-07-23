import Vue from 'vue'

import { Module } from 'vuex'
import { Context as RootContext, RootState } from '@/store/typing'
import { Parent } from '@/utils/domain/bases/interfaces'
import { ID } from '@/utils/domain/types'
import { CrossSectionsState } from '@/store/modules/gaussianRandomFields/typing'
import { Optional } from '@/utils/typing'

import CrossSection, {
  CrossSectionSerialization
} from '@/utils/domain/gaussianRandomField/crossSection'
import { DEFAULT_CROSS_SECTION } from '@/config'
import { getId } from '@/utils'
import { APSError } from '@/utils/domain/errors'

type Context = RootContext<CrossSectionsState, RootState>

async function updateAffectedFields ({ state, rootGetters, dispatch }: Context, id: ID): Promise<void> {
  const crossSection = state.available[`${id}`]
  const relevantFields = Object.values(rootGetters.allFields.filter((field): boolean => field.isChildOf(crossSection.parent)))
  await Promise.all(relevantFields
    .map((field): Promise<void> => dispatch('gaussianRandomFields/updateSimulation', { grfId: field.id }, { root: true }))
  )
}

const module: Module<CrossSectionsState, RootState> = {
  namespaced: true,

  state: {
    available: {},
  },

  actions: {
    async fetch ({ state, dispatch, rootGetters }, { zone = null, region = null } = {}): Promise<CrossSection | undefined> {
      const parent = {
        zone: zone || rootGetters.zone,
        region: region || rootGetters.region,
      }
      await dispatch('add', {
        type: DEFAULT_CROSS_SECTION.type,
        relativePosition: DEFAULT_CROSS_SECTION.position,
        parent,
      })
      return Object.values(state.available)
        .find((setting): boolean => setting.isChildOf({ zone, region }))
    },
    async populate ({ commit, dispatch, getters, rootState }, crossSections: CrossSection | CrossSectionSerialization): Promise<void> {
      for (const crossSection of Object.values(crossSections)) {
        const existing = getters['byParent'](crossSection)
        if (existing && existing.id !== crossSection.id) {
          if (Object.values(rootState.gaussianRandomFields.available).some((field): boolean => field.settings.crossSection.id === existing.id)) {
            throw new APSError('There is a conflict with the cross sections')
          }
          commit('DELETE', existing)
        }
        await dispatch('add', crossSection)
      }
    },
    add ({ commit, getters }, crossSection): void {
      const existing = getters['byParent'](crossSection)
      if (!existing) {
        commit('ADD', new CrossSection({ ...crossSection }))
      }
    },
    async remove ({ commit, dispatch, rootState }, crossSection): Promise<void> {
      await Promise.all(Object.values(rootState.gaussianRandomFields.available)
        .filter((field): boolean => getId(field.settings.crossSection) === getId(crossSection))
        .map((field): Promise<void> => dispatch('gaussianRandomFields/remove', field, { root: true })))
      commit('DELETE', crossSection)
    },
    async changeType (context, { id, type }): Promise<void> {
      const { commit } = context
      commit('CHANGE_TYPE', { id, type })
      await updateAffectedFields(context, id)
    },
    async changeRelativePosition (context, { id, relativePosition }): Promise<void> {
      const { commit } = context
      commit('CHANGE_RELATIVE_POSITION', { id, relativePosition })
      await updateAffectedFields(context, id)
    },
  },

  mutations: {
    ADD (state, crossSection): void {
      Vue.set(state.available, crossSection.id, crossSection)
    },
    DELETE (state, crossSection): void {
      Vue.delete(state.available, crossSection.id)
    },
    CHANGE_TYPE (state, { id, type }): void {
      Vue.set(state.available[`${id}`], 'type', type)
    },
    CHANGE_RELATIVE_POSITION (state, { id, relativePosition }): void {
      Vue.set(state.available[`${id}`], 'relativePosition', relativePosition)
    },

  },

  getters: {
    current (state, getters, rootState, rootGetters): Optional<CrossSection> {
      return Object.values(state.available)
        .find((crossSection): boolean => crossSection.isChildOf({ zone: rootGetters.zone, region: rootGetters.region }))
      || null
    },
    byParent: (state): ({ parent }: { parent: Parent }) => Optional<CrossSection> => ({ parent }: { parent: Parent }): Optional<CrossSection> => {
      return Object.values(state.available)
        .find((item): boolean => item.isChildOf(parent)) || null
    },
    byId: (state): (id: ID) => CrossSection => (id: ID): CrossSection => {
      return state.available[`${getId(id)}`]
    }
  },
}

export default module

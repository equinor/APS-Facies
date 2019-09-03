import Vue from 'vue'

import { Module } from 'vuex'
import { RootState } from '@/store/typing'
import { FaciesGroupState } from '@/store/modules/facies/typing'
import { FaciesGroupConfiguration } from '@/utils/domain/facies/group'
import { Identifiable } from '@/utils/domain/bases/interfaces'
import { ID } from '@/utils/domain/types'

import { Facies, FaciesGroup, GlobalFacies, Parent } from '@/utils/domain'
import { getId } from '@/utils/helpers'
import { toIdentifiedObject } from '@/utils'

const module: Module<FaciesGroupState, RootState> = {
  namespaced: true,

  state: {
    available: {},
  },

  actions: {
    async populate ({ commit, rootGetters }, groups: FaciesGroupConfiguration[]): Promise<void> {
      groups.forEach((group): void => {
        group.facies = group.facies.map((facies): Facies => rootGetters['facies/byId'](getId(facies)))
      })
      groups = groups.map((group): FaciesGroup => new FaciesGroup(group))
      groups.forEach((group): void => {
        if (group.facies.some((facies): boolean => !rootGetters['facies/byId'](facies))) {
          throw new Error(`The group reference a facies that does not exist`)
        }
      })
      commit('AVAILABLE', toIdentifiedObject(groups))
    },
    async get ({ getters, dispatch }, { facies, parent }): Promise<FaciesGroup> {
      let group = getters['byFacies'](facies, parent)
      if (!group) {
        group = await dispatch('add', { facies, parent })
      }
      return group
    },
    async add ({ commit, getters, rootGetters }, { facies, parent, id = undefined }: { facies: (GlobalFacies | Identifiable)[], parent: Parent, id?: ID }): Promise<FaciesGroup> {
      // TODO: Deal with missing parents
      // TODO: ensure that none of the given facies are used
      if (!Array.isArray(facies)) facies = [facies]
      if (facies.some((facies): boolean => getters.used(facies))) {
        throw new Error(`The facies, ${facies}, has already been specified`)
      }
      const group = new FaciesGroup({
        id,
        facies: facies.map((facies): Facies => facies instanceof GlobalFacies ? facies : rootGetters['facies/byId'](facies)),
        ...parent,
      })
      commit('ADD', group)
      return group
    },
    remove ({ commit }, group): void {
      commit('DELETE', group)
    },
    update ({ commit }, { group, facies }): void {
      commit('UPDATE', { group, facies })
    }
  },

  mutations: {
    ADD: (state, group): void => {
      Vue.set(state.available, group.id, group)
    },
    DELETE: (state, group): void => {
      Vue.delete(state.available, group.id)
    },
    AVAILABLE: (state, items): void => {
      Vue.set(state, 'available', items)
    },
    UPDATE: (state, { group, facies }): void => {
      Vue.set(state.available[`${group.id}`], 'facies', facies)
    },
  },

  getters: {
    byId: (state) => (id: ID): FaciesGroup | undefined => {
      return state.available[`${getId(id)}`]
    },
    byFacies: (state) => (facies: Facies[], parent: Parent): FaciesGroup | undefined => {
      return Object.values(state.available).find((group): boolean => group.isChildOf(parent) && group.contains(facies))
    },
    used: (state): (facies: Facies) => boolean => (facies: Facies): boolean => {
      const used = new Set()
      Object.values(state.available)
        .forEach((group): void => {
          group.facies.forEach((facies): void => {
            used.add(getId(facies))
          })
        })
      return used.has(getId(facies))
    },
    text: (state, getters, rootState, rootGetters): (group: FaciesGroup) => string => (group: FaciesGroup): string => {
      return group.facies
        .map((facies): string => rootGetters['facies/name'](facies))
        .reduce((text, name) => text ? `${text}, ${name}` : name, '')
    }
  },
}

export default module

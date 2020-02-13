import Vue from 'vue'

import { GlobalFaciesState } from '@/store/modules/facies/typing'
import { Context, RootState } from '@/store/typing'
import { GlobalFacies } from '@/utils/domain'
import { Color } from '@/utils/domain/facies/helpers/colors'
import { RmsFacies } from '@/api/types'
import { Identified } from '@/utils/domain/bases/interfaces'
import { APSTypeError } from '@/utils/domain/errors'
import { Module } from 'vuex'

import rms from '@/api/rms'
import { isEmpty, makeData } from '@/utils'

function getColor ({ rootGetters }: Context<GlobalFaciesState, RootState>, code: number): Color {
  return rootGetters['constants/faciesColors/byCode'](code)
}

async function getFaciesFromRMS ({ rootGetters, rootState }: Context<GlobalFaciesState, RootState>): Promise<RmsFacies[]> {
  return rms.facies(
    rootGetters.gridModel,
    rootGetters.blockedWellParameter,
    rootGetters.blockedWellLogParameter,
    rootState.regions.use ? rootGetters.regionParameter : '__REGIONS_NOT_IN_USE__',
  )
}

function findExisting (items: Identified<GlobalFacies> | GlobalFacies[], { code, name }: { code: number, name: string }): GlobalFacies | undefined {
  items = Array.isArray(items) ? items : Object.values(items)
  return items
    .find((facies): boolean => facies.code === code || facies.name === name)
}

interface FaciesSpecification extends RmsFacies {
  color?: Color
}

const module: Module<GlobalFaciesState, RootState> = {
  namespaced: true,

  state: {
    available: {},
    current: null,
    _loading: false,
    _inRms: [],
  },

  actions: {
    fetch: async (context): Promise<void> => {
      const { commit, dispatch } = context
      commit('AVAILABLE', {})
      commit('IN_RMS', [])

      commit('LOADING', true)
      const facies = await getFaciesFromRMS(context)
      commit('LOADING', false)
      await dispatch('populate', facies)
      commit('IN_RMS', facies)
    },
    populate: async (context, facies: FaciesSpecification[]): Promise<void> => {
      const { commit, state } = context

      const minFaciesCode = facies
        .map(({ code }): number => code)
        .reduce((min, curr): number => min < curr ? min : curr, Number.POSITIVE_INFINITY)
      facies.forEach((facies): void => {
        if (!facies.color) {
          facies.color = getColor(context, facies.code - minFaciesCode)
        }
      })
      const data = makeData(facies, GlobalFacies, state.available)
      commit('AVAILABLE', data)
    },
    refresh: async (context): Promise<void> => {
      const { state, commit, dispatch } = context
      const existingFacies = Object.values(state.available)
        .reduce((mapping, facies) => {
          mapping[facies.code] = facies
          return mapping
        }, ({} as {[code: number]: GlobalFacies}))
      const faciesConfigurations = (await getFaciesFromRMS(context))
      await Promise.all(faciesConfigurations
        .filter(({ code }): boolean => !existingFacies[`${code}`])
        .map(config => dispatch('new', config))
      )
      commit('REFRESH', faciesConfigurations)
    },
    new: async (context, { code, name, color, observed }): Promise<GlobalFacies> => {
      const { commit, state } = context
      if (isEmpty(code) || code < 0) {
        code = 1 + Object.values(state.available)
          .concat(state._inRms)
          .map(facies => facies.code)
          .reduce((a, b) => Math.max(a, b), 0)
      }
      if (isEmpty(name)) {
        name = `F${code}`
      }
      if (isEmpty(color)) {
        color = getColor(context, code)
      }
      if (findExisting(state._inRms, { code, name })) {
        throw new APSTypeError(`There already exists a facies with code = ${code}, or name = ${name} in RMS`)
      }
      const facies = new GlobalFacies({ code, name, color, observed })
      commit('ADD', facies)
      return facies
    },
    current: async ({ commit }, { id }): Promise<void> => {
      commit('CURRENT', { id })
    },
    removeSelectedFacies: async ({ commit, dispatch, state }): Promise<void> => {
      if (state.current) {
        commit('REMOVE', { id: state.current })
        await dispatch('current', { id: null })
      }
    },
    changeColorPallet: async ({ dispatch, state }, mapping: Map<Color, Color>): Promise<void> => {
      await Promise.all(Object.values(state.available)
        .map(facies => dispatch('changeColor', { id: facies.id, color: mapping.get(facies.color) })))
    },
    changeColor: async ({ commit }, { id, color }): Promise<void> => {
      commit('CHANGE', { id, name: 'color', value: color })
    },
    changeName: async ({ commit }, { id, name }): Promise<void> => {
      commit('CHANGE', { id, name: 'name', value: name })
    },
    changeAlias: async ({ commit }, { id, alias }): Promise<void> => {
      commit('CHANGE', { id, name: 'alias', value: alias })
    },
    changeCode: async ({ commit }, { id, code }): Promise<void> => {
      commit('CHANGE', { id, name: 'code', value: code })
    }
  },

  mutations: {
    AVAILABLE: (state, facies): void => {
      Vue.set(state, 'available', facies)
    },
    CURRENT: (state, { id }): void => {
      state.current = id
    },
    LOADING: (state, toggle): void => {
      Vue.set(state, '_loading', toggle)
    },
    ADD: (state, facies): void => {
      Vue.set(state.available, facies.id, facies)
    },
    REMOVE: (state, { id }): void => {
      Vue.delete(state.available, id)
    },
    CHANGE: (state, { id, name, value }): void => {
      Vue.set(state.available[`${id}`], name, value)
    },
    IN_RMS: (state, facies): void => {
      Vue.set(state, '_inRms', facies)
    },
    REFRESH: (state, faciesConfigurations: RmsFacies[]): void => {
      // Update global facies in place, to preserve references, and thus comparison between GlobalFacies
      // and anything else, that might reference one (such as Facies, FaciesGroup, and truncation rules, though polygons)
      // PS: Doing this functionally, i.e. creating new objects, quickly became complex, once the truncation rules
      //     had to be created anew as well
      Object.values(state.available).forEach(facies => {
        Object.assign(facies, faciesConfigurations.find(({ code }) => facies.code === code) || {})
      })
    },
  },

  getters: {
    selected: (state, getters, rootState, rootGetters): GlobalFacies[] => {
      return rootGetters['facies/selected']
        .map(({ facies }: { facies: GlobalFacies }): GlobalFacies => state.available[`${facies.id}`])
    },
  },
}

export default module

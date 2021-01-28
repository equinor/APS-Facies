import { FaciesState } from '@/store/modules/facies/typing'
import { RootState } from '@/store/typing'
import { resolveParentReference } from '@/store/utils'
import { Region, Parent } from '@/utils/domain'
import { Identifiable } from '@/utils/domain/bases/interfaces'
import TruncationRule from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'
import { Optional } from '@/utils/typing'
import Vue from 'vue'

import { divide } from 'mathjs'

import { isNumber } from 'lodash'

import rms from '@/api/rms'

import Facies, { FaciesSerialization, ProbabilityCube } from '@/utils/domain/facies/local'
import GlobalFacies from '@/utils/domain/facies/global'

import {
  notEmpty,
  hasCurrentParents,
  hasParents,
  parentId,
} from '@/utils'

import { Dispatch, Module } from 'vuex'
import global from './global'
import groups from './groups'
import { getId, identify, isUUID } from '@/utils/helpers'

function updateFaciesProbability (dispatch: Dispatch, facies: Facies, probability: number): Promise<void> {
  return dispatch('changePreviewProbability', { facies, previewProbability: probability })
}

const module: Module<FaciesState, RootState> = {
  namespaced: true,

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  state: {
    available: {},
    constantProbability: {},
  },

  modules: {
    global,
    groups,
  },

  actions: {
    add: ({ commit, getters }, { facies, parent, probabilityCube = null, previewProbability = null, id = null }): Facies => {
      const localFacies = new Facies({
        id,
        facies: (facies instanceof GlobalFacies) ? facies : getters.byId(facies),
        probabilityCube,
        previewProbability,
        parent,
      })
      commit('ADD', { facies: localFacies })
      return localFacies
    },
    remove: ({ commit }, facies: Facies): void => {
      commit('REMOVE', { facies })
    },
    select: async ({ commit, dispatch, state }, { items, parent }: { items: Identifiable[], parent: Parent }): Promise<void> => {
      const getRelevantFacies = (): Facies[] => Object.values(state.available)
        .filter((facies): boolean => hasParents(facies, parent.zone, parent.region))

      let removed = false
      const relevantFacies = getRelevantFacies()
      items.forEach((global): void => {
        if (!relevantFacies.map(({ facies }): ID => getId(facies)).includes(getId(global))) {
          commit('ADD', { facies: new Facies({ facies: state.global.available[`${getId(global)}`], ...parent }) })
        }
      })
      relevantFacies.forEach((facies): void => {
        if (!items.map(getId).includes(getId(facies.facies))) {
          commit('REMOVE', { facies })
          removed = true
        }
      })
      if (removed) {
        await dispatch('normalize', { selected: getRelevantFacies() })
      }
      await dispatch('zones/touch', parent, { root: true })
    },
    selectObserved: async ({ dispatch, state, getters, rootGetters, rootState }): Promise<void> => {
      if (rootGetters.loading) return undefined
      if (!rootState.options.automaticObservedFaciesSelection.value) return undefined

      const { zone, region }: Parent = rootGetters
      const parentDefined: boolean = rootGetters.useRegions ? !!region : !!zone
      if (parentDefined && getters.isFaciesFetchedFromRMS) {
        const parent = { zone, region }
        const touched: boolean = rootGetters.useRegions ? (region as Region).touched : zone.touched
        if (!touched) {
          const observedFacies = Object.values(state.global.available)
            .filter((facies): boolean => facies.isObserved(parent) && getters.isFromRMS(facies))
          if (observedFacies.length > 0) {
            await dispatch('select', {
              items: observedFacies,
              parent,
            })
          }
        }
      }
    },
    populate: (context, facies: FaciesSerialization[]): void => {
      const { commit, getters } = context
      const instances = facies.map(config => new Facies({
        ...config,
        facies: getters.byId(getId(config.facies)),
        parent: resolveParentReference(context, config.parent),
      }))
      commit('AVAILABLE', identify(instances))
    },
    updateProbabilities: async ({ dispatch, state }, { probabilityCubes, parent }): Promise<void> => {
      if (notEmpty(probabilityCubes)) {
        const facies = Object.values(state.available)
          .filter((facies): boolean => facies.isChildOf(parent) && !!facies.probabilityCube)
        await Promise.all(facies.map((facies): Promise<void> => updateFaciesProbability(dispatch, facies, probabilityCubes[`${facies.probabilityCube}`])))
        await dispatch('normalize', { selected: facies })
      }
    },
    updateProbability: ({ dispatch, state, getters }, { facies, probability }): Promise<void> => {
      if (!facies.id) {
        facies = state.available[`${facies}`] || getters.selected.find((item: Facies): boolean => item.facies === facies)
      }
      return updateFaciesProbability(dispatch, facies, probability)
    },
    normalizeEmpty: async ({ dispatch, getters }): Promise<void> => {
      const selectedFacies: Facies[] = getters.selected
      const probabilities = selectedFacies
        .map((facies): number => facies.previewProbability ? facies.previewProbability : 0)
      const emptyProbability = (1 - probabilities.reduce((sum: number, prob: number): number => sum + prob, 0)) / probabilities.filter((prob: number): boolean => prob === 0).length
      await Promise.all(selectedFacies
        .map((facies): Promise<void> => !facies.previewProbability
          ? updateFaciesProbability(dispatch, facies, emptyProbability)
          : new Promise((resolve) => resolve()))
      )
    },
    averageProbabilityCubes: async (
      { dispatch, state, rootGetters },
      {
        probabilityCubes = null,
        gridModel = null,
        zoneNumber = null,
        useRegions = null,
        regionParameter = null,
        regionNumber = null,
      } = {}
    ): Promise<void> => {
      if (!gridModel) gridModel = rootGetters.gridModel
      if (!zoneNumber && zoneNumber !== 0) zoneNumber = rootGetters.zone.code
      if (!useRegions && useRegions !== false) useRegions = rootGetters.useRegions
      if (useRegions) {
        if (!regionParameter) regionParameter = rootGetters.regionParameter
        const region = rootGetters.region
        if (region && !regionNumber && regionNumber !== 0) regionNumber = region.code
      }
      const parent = rootGetters['zones/byCode'](zoneNumber, useRegions ? regionNumber : null)
      if (!probabilityCubes) {
        probabilityCubes = Object.values(state.available)
          .filter((facies): boolean => facies.isChildOf(parent))
          .map((facies): ProbabilityCube | null => facies.probabilityCube)
          .filter((param): boolean => notEmpty(param))
      }

      probabilityCubes = await rms.averageProbabilityCubes(gridModel, probabilityCubes, zoneNumber, regionParameter, regionNumber)
      // Result in the form of { probCubeName_1: average, ...}
      await dispatch('updateProbabilities', { probabilityCubes, parent })
    },
    normalize: async ({ dispatch, getters }, { selected = null }: { selected?: Optional<Facies[]> } = {}): Promise<void> => {
      selected = (selected || getters.selected) as Facies[]
      const cumulativeProbability = selected
        .map((facies): number | null => facies.previewProbability)
        .reduce((sum: number, prob: number | null): number => sum + (prob || 0), 0)
      await Promise.all(selected
        .filter((facies): boolean => facies.previewProbability !== null)
        .map((facies): Promise<void> => {
          const probability = !cumulativeProbability
            ? divide(1, (selected as Facies[]).length)
            : divide(facies.previewProbability || 0, cumulativeProbability)
          return updateFaciesProbability(dispatch, facies, probability)
        }))
    },
    populateConstantProbability: ({ commit }, data): void => {
      Object.keys(data).forEach((parentId): void => {
        commit('CONSTANT_PROBABILITY', { parentId, toggled: data[`${parentId}`] })
      })
    },
    toggleConstantProbability: ({ commit, getters, rootGetters }): void => {
      const _id = parentId({ zone: rootGetters.zone, region: rootGetters.region })
      const usage = !getters.constantProbability()
      commit('CONSTANT_PROBABILITY', { parentId: _id, toggled: usage })
    },
    setConstantProbability: ({ commit }, { parentId, toggled }): void => {
      if (typeof toggled === 'boolean') {
        commit('CONSTANT_PROBABILITY', { parentId, toggled })
      }
    },
    changeProbabilityCube: ({ commit }, { facies, probabilityCube }): void => {
      commit('CHANGE_PROBABILITY_CUBE', { facies, probabilityCube })
    },
    changePreviewProbability: ({ commit }, { facies, previewProbability }): void => {
      commit('CHANGE_PREVIEW_PROBABILITY', { facies, previewProbability })
    },
    fetch: async ({ dispatch }): Promise<void> => {
      await dispatch('global/fetch')
    },
  },

  mutations: {
    ADD: (state, { facies }): void => {
      Vue.set(state.available, facies.id, facies)
    },
    // TODO: Take `facies` as input, and not an object
    REMOVE: (state, { facies }): void => {
      Vue.delete(state.available, facies.id)
    },
    AVAILABLE: (state, facies): void => {
      Vue.set(state, 'available', facies)
    },
    SELECTED: (state, { id, toggled }): void => {
      Vue.set(state.available[`${id}`], 'selected', toggled)
    },
    UPDATE: (state, facies): void => {
      Vue.set(state.available, facies.id, facies)
    },
    CONSTANT_PROBABILITY: (state, { parentId, toggled }): void => {
      Vue.set(state.constantProbability, parentId, toggled)
    },
    CHANGE_PROBABILITY_CUBE: (state, { facies, probabilityCube }): void => {
      state.available[`${facies.id}`].probabilityCube = probabilityCube
    },
    CHANGE_PREVIEW_PROBABILITY: (state, { facies, previewProbability }): void => {
      state.available[`${facies.id}`].previewProbability = previewProbability
    },
  },

  getters: {
    name: (state, getters): (id: ID | Identifiable) => string | string[] => (id: ID | Identifiable): string | string[] => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      id = isUUID(id) ? id : id.id
      const facies: Facies | Facies[] = getters.byId(id)
      if (facies instanceof Array) {
        return facies.map((id): string => getters.name(id))
      }
      return facies.name || getters.byId(facies.facies).name
    },
    byId: (state, getters): (id: ID | undefined) => Facies | Facies[] | null => (id: ID | undefined): Facies | Facies[] | null => {
      id = getId(id)
      const facies = state.available[`${id}`] || state.global.available[`${id}`]
      if (!facies) {
        const group = getters['groups/byId'](id)
        return group && group.facies.map(getters.byId)
      } else {
        return facies || null
      }
    },
    byName: (state): (name: string) => Facies | undefined => (name: string): Facies | undefined => {
      return Object.values(state.available).find((facies): boolean => facies.name === name)
    },
    constantProbability: (state, getters, rootState, rootGetters): (parent: Parent) => number | boolean => (parent: Parent): number | boolean => {
      parent = parent || { zone: rootGetters.zone, region: rootGetters.region }
      const constantProbability = (): number => state.constantProbability[`${parentId(parent)}`]

      return !parent.zone || typeof constantProbability() === 'undefined'
        ? true
        : constantProbability()
    },
    selected: (state, getters, rootState, rootGetters): Facies[] => {
      return Object.values(state.available)
        .filter((facies): boolean => hasCurrentParents(facies, rootGetters))
        .sort((a, b): number => a.facies.code - b.facies.code)
    },
    cumulative: (state, getters): number => {
      return getters.selected
        .map((facies: Facies): number | null => facies.previewProbability)
        .reduce((sum: number, prob: number): number => sum + prob, 0)
    },
    unset: (state, getters): boolean => {
      return getters.selected.every((facies: Facies): boolean => !isNumber(facies.previewProbability))
    },
    availableForBackgroundFacies: <S, R, T extends TruncationRule>(state: S, getters: R): (rule: T, facies: Facies) => boolean => (rule: T, facies: Facies): boolean => {
      return !getters['groups/used'](facies)
        && rule.backgroundPolygons.map(({ facies }): ID => getId(facies)).includes(getId(facies))
    },
    isFromRMS: (state): (facies: GlobalFacies) => boolean => (facies: GlobalFacies): boolean => {
      return facies
        ? !!state.global._inRms.find(({ code, name }): boolean => facies.code === code && facies.name === name)
        : false
    },
    isFaciesFetchedFromRMS: (state, getters, rootState, rootGetters): boolean => {
      return !!rootGetters.blockedWellParameter && !!rootGetters.blockedWellLogParameter
    }
  },
}

export default module

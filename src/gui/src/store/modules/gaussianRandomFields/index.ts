import { Context as RootContext, RootState } from '@/store/typing'
import { Region } from '@/utils/domain'
import { Identified } from '@/utils/domain/bases/interfaces'
import { ID } from '@/utils/domain/types'
import Zone from '@/utils/domain/zone'
import Vue from 'vue'

import { getId, hasParents, newSeed } from '@/utils'
import {
  Trend,
  Variogram,
  GaussianRandomField,
  GaussianRandomFieldSerialization
} from '@/utils/domain/gaussianRandomField'

import crossSections from '@/store/modules/gaussianRandomFields/crossSections'
import rms from '@/api/rms'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import { unpackVariogram } from '@/utils/domain/gaussianRandomField/variogram'
import { unpackTrend } from '@/utils/domain/gaussianRandomField/trend'
import { Module } from 'vuex'

interface GaussianRandomFieldState {
  fields: Identified<GaussianRandomField>
}

type Context = RootContext<GaussianRandomFieldState, RootState>

function setValue (
  { state, commit }: Context,
  { commitName, grfId, type, legalTypes, variogramOrTrend, value }: { commitName: string, grfId: ID, type?: string, legalTypes?: string[], variogramOrTrend?: 'variogram' | 'trend', value: any }
): void {
  const checks: ([() => boolean, string])[] = [
    [
      (): boolean => state.fields.hasOwnProperty(grfId),
      `The gaussian field (${grfId}) does not exists`
    ],
    [
      // @ts-ignore
      (): boolean => typeof type === 'undefined' || legalTypes.indexOf(type) !== -1,
      `The type '${type}' is not a legal value (${legalTypes})`
    ],
    [
      (): boolean => typeof variogramOrTrend === 'undefined' || ['variogram', 'trend'].indexOf(variogramOrTrend) >= 0,
      `When specifying 'variogramOrTrend', is MUST be either 'variogram', or 'trend'`
    ],
  ]
  checks.forEach(([check, errorMessage]): void => {
    if (!check()) throw new Error(errorMessage)
  })
  commit(commitName, { grfId, type, variogramOrTrend, value })
}

function getRelevantFields (state: GaussianRandomFieldState, zone: Zone, region: Region): GaussianRandomField[] {
  const zoneId = zone.id || zone
  const regionId = region ? (region.id || region) : null
  return Object.values(state.fields)
    .filter((field): boolean => hasParents(field, zoneId, regionId))
}

function newGaussianFieldName (state: GaussianRandomFieldState, zone: Zone, region: Region): string {
  const name = (num: number): string => `GRF${num}`
  const relevant = (): GaussianRandomField[] => getRelevantFields(state, zone, region)

  let grfNumber = relevant().length + 1
  while (relevant().find((field): boolean => field.name === name(grfNumber))) {
    grfNumber += 1
  }
  return name(grfNumber)
}

const module: Module<GaussianRandomFieldState, RootState> = {
  namespaced: true,

  state: {
    fields: {
    },
  },

  modules: {
    crossSections,
  },

  actions: {
    async populate ({ dispatch }, fields: (GaussianRandomField | GaussianRandomFieldSerialization)[]): Promise<void> {
      await Promise.all(fields.map((field): Promise<void> => {
        return dispatch('add', field)
      }))
    },
    async addEmptyField ({ dispatch, state, rootGetters }, { zone, region } = {}): Promise<GaussianRandomField> {
      zone = zone || rootGetters.zone
      region = region || rootGetters.region
      const field = new GaussianRandomField({
        name: newGaussianFieldName(state, zone, region),
        crossSection: await dispatch('crossSections/fetch', { zone, region }),
        zone,
        region,
      })
      await dispatch('add', field)
      return field
    },
    add ({ commit, getters }, field): void {
      if (!(field instanceof GaussianRandomField)) {
        field = new GaussianRandomField({
          ...field,
          variogram: new Variogram(unpackVariogram(field.variogram)),
          trend: new Trend(unpackTrend(field.trend)),
          crossSection: getters['crossSections/byId'](field.settings.crossSection),
        })
      }
      commit('ADD', field)
    },
    async remove ({ commit, dispatch }, field): Promise<void> {
      await dispatch('truncationRules/deleteField', { grfId: field.id }, { root: true })
      commit('DELETE', { grfId: getId(field) })
    },
    async deleteField ({ state, commit, dispatch }, { grfId }): Promise<void> {
      if (state.fields.hasOwnProperty(grfId)) {
        await dispatch('truncationRules/deleteField', { grfId }, { root: true })
        commit('DELETE', { grfId })
      }
    },
    async updateSimulation ({ state, commit, dispatch, rootGetters }, { grfId }): Promise<void> {
      const field = state.fields[`${grfId}`]
      commit('CHANGE_WAITING', { grfId, value: true })
      try {
        await dispatch('updateSimulationData', {
          grfId: grfId,
          data: await rms.simulateGaussianField({
            name: field.name,
            variogram: field.variogram,
            trend: field.trend,
            settings: rootGetters['simulationSettings'](grfId),
          })
        })
      } finally {
        commit('CHANGE_WAITING', { grfId, value: false })
      }
    },
    updateSimulationData (context, { grfId, data }): void {
      setValue(context, { grfId, value: data, commitName: 'CHANGE_SIMULATION' })
    },
    changeName (context, { grfId, name }): void {
      setValue(context, { grfId, value: name, commitName: 'CHANGE_NAME' })
    },
    changeSettings (context, { grfId, settings }): void {
      setValue(context, { grfId, value: settings, commitName: 'CHANGE_SETTINGS' })
    },
    newSeed (context, { grfId }): void {
      setValue(context, { grfId, value: newSeed(), commitName: 'CHANGE_SEED' })
    },
    seed (context, { grfId, value }): void {
      setValue(context, { grfId, value, commitName: 'CHANGE_SEED' })
    },
    overlay (context, { grfId, value }): void {
      setValue(context, { grfId, value, commitName: 'CHANGE_OVERLAY' })
    },
    // TODO: check values are appropriate
    // Variogram
    range (context, { grfId, type, value }): void {
      setValue(context, { grfId, type, value, legalTypes: ['main', 'perpendicular', 'vertical'], commitName: 'CHANGE_RANGE' })
    },
    angle (context, { grfId, variogramOrTrend, type, value }): void {
      const legalTypes = variogramOrTrend === 'variogram' ? ['azimuth', 'dip'] : ['azimuth', 'stacking', 'migration']
      setValue(context, { grfId, type, variogramOrTrend, value, legalTypes, commitName: 'CHANGE_ANGLE' })
    },
    variogramType (context, { grfId, value }): void {
      const { rootState } = context
      setValue(context, { grfId, value, type: value, legalTypes: rootState.constants.options.variograms.available, commitName: 'CHANGE_VARIOGRAM_TYPE' })
    },
    power (context, { grfId, value }): void {
      setValue(context, { grfId, value, commitName: 'CHANGE_POWER' })
    },
    // Trend
    useTrend (context, { grfId, value }): void {
      setValue(context, { grfId, variogramOrTrend: 'trend', value, commitName: 'USE_TREND' })
    },
    relativeStdDev (context, { grfId, value }): void {
      setValue(context, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RELATIVE_STANDARD_DEVIATION' })
    },
    relativeSize (context, { grfId, value }): void {
      setValue(context, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RELATIVE_SIZE_OF_ELLIPSE' })
    },
    async trendType (context, { grfId, value }): Promise<void> {
      const { dispatch, state, rootState } = context
      setValue(context, { grfId, variogramOrTrend: 'trend', value, type: value, legalTypes: rootState.constants.options.trends.available, commitName: 'CHANGE_TREND_TYPE' })
      const field = state.fields[`${grfId}`]
      if (field.trend.type === 'HYPERBOLIC') {
        const curvature = field.trend.curvature
        if (curvature.value <= 1) {
          await dispatch('curvature', { grfId, value: new FmuUpdatableValue(1.01, curvature.updatable) })
        }
      }
    },
    trendParameter (context, { grfId, value }): void {
      setValue(context, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RMS_TREND_PARAM' })
    },
    stackingDirection (context, { grfId, value }): void {
      setValue(context, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_STACKING_DIRECTION' })
    },
    curvature (context, { grfId, value }): void {
      setValue(context, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_CURVATURE' })
    },
    originType (context, { grfId, value }): void {
      const { rootState } = context
      setValue(context, { grfId, variogramOrTrend: 'trend', value, type: value, legalTypes: rootState.constants.options.origin.available, commitName: 'CHANGE_ORIGIN_TYPE' })
    },
    origin (context, { grfId, type, value }): void {
      setValue(context, { grfId, variogramOrTrend: 'trend', type, value, legalTypes: ['x', 'y', 'z'], commitName: 'CHANGE_ORIGIN_COORDINATE' })
    },
  },

  mutations: {
    // Gaussian Random Field
    ADD (state, field): void {
      Vue.set(state.fields, field.id, field)
    },
    DELETE (state, { grfId }): void {
      Vue.delete(state.fields, grfId)
    },
    CHANGE_NAME (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`], 'name', value)
    },
    CHANGE_SETTINGS (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`], 'settings', value)
    },
    CHANGE_SEED (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].settings, 'seed', value)
    },
    CHANGE_SIMULATION (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`], '_data', value)
    },
    CHANGE_OVERLAY (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`], 'overlay', value)
    },
    CHANGE_WAITING (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`], 'waiting', value)
    },
    // Variogram
    CHANGE_RANGE (state, { grfId, type, value }): void {
      Vue.set(state.fields[`${grfId}`].variogram.range, type, value)
    },
    CHANGE_ANGLE (state, { grfId, variogramOrTrend, type, value }): void {
      Vue.set(state.fields[`${grfId}`][`${variogramOrTrend}`].angle, type, value)
    },
    CHANGE_VARIOGRAM_TYPE (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].variogram, 'type', value)
    },
    CHANGE_POWER (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].variogram, 'power', value)
    },
    // Trend
    USE_TREND (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].trend, 'use', value)
    },
    CHANGE_TREND_TYPE (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].trend, 'type', value)
    },
    CHANGE_RELATIVE_STANDARD_DEVIATION (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].trend, 'relativeStdDev', value)
    },
    CHANGE_RELATIVE_SIZE_OF_ELLIPSE (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].trend, 'relativeSize', value)
    },
    CHANGE_STACKING_DIRECTION (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].trend, 'stackingDirection', value)
    },
    CHANGE_CURVATURE (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].trend, 'curvature', value)
    },
    CHANGE_ORIGIN_COORDINATE (state, { grfId, type, value }): void {
      Vue.set(state.fields[`${grfId}`].trend.origin, type, value)
    },
    CHANGE_ORIGIN_TYPE (state, { grfId, value }): void {
      Vue.set(state.fields[`${grfId}`].trend.origin, 'type', value)
    },
    CHANGE_RMS_TREND_PARAM (state, { grfId, value }): void {
      state.fields[`${grfId}`].trend.parameter = value
    }
  },

  getters: {
    byId: (state): (id: ID) => GaussianRandomField | undefined => (id: ID): GaussianRandomField | undefined => {
      return state.fields[`${getId(id)}`]
    },
  },
}

export default module

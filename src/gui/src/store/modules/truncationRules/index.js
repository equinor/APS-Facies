import Vue from 'vue'
import cloneDeep from 'lodash/cloneDeep'
import uuidv4 from 'uuid/v4'

import api from '@/api/rms'

import templates from '@/store/modules/truncationRules/templates'

import { Bayfill, NonCubic } from '@/store/utils/domain/truncationRule'
import { ADD_ITEM } from '@/store/mutations'
import { addItem } from '@/store/actions'
import {
  notEmpty,
  isEmpty,
  hasCurrentParents,
  hasEnoughFacies,
  resolve,
  allSet,
  makeTruncationRuleSpecification,
} from '@/utils'

const changePreset = (state, thing, item) => {
  Vue.set(state.preset, thing, item)
}

const process = (getters, items, target, type, path) => {
  return items.map(item => {
    const updated = {
      ...item,
    }
    updated[`${target}`] = getters.id(type, resolve(path, item))
    return updated
  })
}

const processOverlay = (getters, overlay) => {
  if (!overlay) return null
  const items = {}
  overlay.items.forEach(({ over, polygons }, index) => {
    polygons.forEach(({ field, facies, probability, interval }) => {
      const id = uuidv4()
      items[`${id}`] = {
        id,
        group: over.map(facies => findFaciesByIndex(getters, facies).id), // TODO: Process properly
        field: findFieldByIndex(getters, field).id,
        facies: findFaciesByIndex(getters, facies).id,
        fraction: probability,
        center: interval,
        order: index,
      }
    })
  })
  return { ...overlay, items }
}

const sortAlphabetically = arr => {
  return Object.values(arr).sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)
}

const findFieldByIndex = (getters, field) => {
  const relevantFields = sortAlphabetically(getters.fields)
  return relevantFields[`${field.index}`]
}

const findFaciesByIndex = (getters, facies) => {
  const relevantFacies = sortAlphabetically(getters.faciesTable).filter(facies => !!facies.selected)
  return relevantFacies[`${facies.index}`]
}

const processFields = (getters, state, fields) => {
  if (state.options.automaticAlphaFieldSelection.value) {
    return fields.map(item => {
      return {
        channel: item.channel,
        field: findFieldByIndex(getters, item.field).id
      }
    })
  } else {
    return process(getters, fields, 'field', 'gaussianRandomField', 'field.name')
  }
}

const processPolygons = (getters, polygons) => {
  const autoFill = true
  if (autoFill) {
    polygons = polygons.map(polygon => {
      return {
        ...polygon,
        facies: findFaciesByIndex(getters, polygon.facies).name,
      }
    })
  }
  return process(getters, polygons, 'facies', 'facies', 'facies')
}

const findPolygonInRule = (rule, polygon) => {
  return rule.polygons[`${polygon.id}`]
}

const setFacies = (polygons, src, dest) => {
  polygons[`${dest.id}`].facies = src.facies
}

function swapFacies (rule, polygons) {
  if (polygons.length !== 2) throw new Error('Only two polygons may be swapped')
  const newPolygons = cloneDeep(rule.polygons)

  const first = findPolygonInRule(rule, polygons[0])
  const other = findPolygonInRule(rule, polygons[1])

  setFacies(newPolygons, first, other)
  setFacies(newPolygons, other, first)

  return newPolygons
}

const setSettingValue = (state, rule, polygon, property, value) => {
  Vue.set(state.rules[`${rule.id}`].settings[`${polygon.id}`], property, value)
}

const setProperty = (state, rule, property, values) => {
  Vue.set(state.rules[`${rule.id}`], property, values)
}

export default {
  namespaced: true,

  state: {
    rules: {},
    preset: {
      type: '',
      template: '',
    },
  },

  modules: {
    templates,
  },

  actions: {
    fetch ({ dispatch }) {
      dispatch('templates/fetch')
    },
    add ({ commit, dispatch, state, rootGetters, rootState }, { type, name, polygons, overlay, fields, settings, parent }) {
      parent = parent || { zone: rootGetters.zone, region: rootGetters.region }
      type = state.templates.types.available[`${type}`].type
      const autoFill = true
      const mapping = {
        'bayfill': Bayfill,
        'non-cubic': NonCubic,
        'cubic': null, // TODO
      }
      if (!mapping.hasOwnProperty(type)) {
        throw new Error(`The truncation rule of type ${type} is not implemented`)
      }
      const rule = new mapping[`${type}`]({
        polygons: processPolygons(rootGetters, polygons),
        fields: processFields(rootGetters, rootState, fields),
        overlay: processOverlay(rootGetters, overlay),
        settings,
        name,
        zone: rootGetters.zone,
        region: rootGetters.region
      })
      const addProportions = (proportions, polygons) => {
        if (isEmpty(polygons)) return proportions
        Object.values(polygons).forEach(({ facies, proportion }) => {
          proportions.push({ facies, probability: proportion || 1 })
        })
        return proportions
      }
      if (autoFill) {
        const normalize = (items) => {
          const sum = items.reduce((sum, { probability }) => sum + probability, 0)
          return items.map(payload => { return { ...payload, probability: payload.probability / sum } })
        }
        let proportions = []
        addProportions(proportions, rule.polygons)
        normalize(proportions).forEach((payload) => {
          dispatch('facies/updateProbability', payload, { root: true })
        })
      }
      return addItem({ commit }, { item: rule })
    },
    remove ({ commit, state, rootGetters }, ruleId) {
      const correctId = _id => isEmpty(_id) || !state.rules.hasOwnProperty(_id)

      if (correctId(ruleId)) {
        ruleId = rootGetters.truncationRule.id
      }

      if (correctId(ruleId)) {
        commit('REMOVE', ruleId)
      } else {
        throw new Error(`The rule with ID ${ruleId} does not exist. Cannot be removed`)
      }
    },
    addPolygon ({ commit, dispatch, store }, { rule, order = null, overlay = false }) {
      if (!order || order < 0) {
        const polygons = Object.values(rule.polygons)
          .filter(polygon => polygon.overlay === overlay)
        order = polygons.length === 0
          ? 0
          : 1 + polygons
            .map(polygon => polygon.order)
            .reduce((max, curr) => curr > max ? curr : max, 0)
      }
      const polygon = {
        id: uuidv4(),
        overlay,
        facies: '',
        proportion: 1, // TODO: ...
        order,
        name: 1 + Object.values(rule.polygons)
          .map(polygon => polygon.name)
          .reduce((max, curr) => curr > max ? curr : max, 0),
      }
      const setting = {
        fraction: 1,
        polygon: polygon.name,
        updatable: false,
      }
      if (overlay) {
        // TODO: Add extra fields, when necessary
        // if (rule.overlayPolygons.length + 1 > rule.fields.length - rule.backgroundFields.length) {
        //   dispatch('gaussianRandomFields/addEmptyField', { zoneId: rule.parent.zone, regionId: rule.parent.region }, { root: true })
        // }
        polygon.center = 0
        polygon.field = ''
        polygon.fraction = 1
        polygon.group = []
      }
      if (rule.type === 'bayfill') {
        throw new Error('Bayfill must have exactly 5 polygons. Cannot add more.')
      } else if (rule.type === 'non-cubic') {
        if (!overlay) {
          setting.angle = 0
        }
      } else if (rule.type === 'cubic') {
        throw new Error('Cubic is not implemented')
      }
      const polygons = cloneDeep(rule.polygons)
      Object.values(polygons).forEach(polygon => {
        if (polygon.order >= order) {
          polygon.order += 1
        }
      })
      polygons[polygon.id] = polygon
      commit('CHANGE_POLYGONS', { rule, polygons })
      commit('ADD_SETTING', { rule, polygon, setting })
    },
    removePolygon ({ commit }, { rule, polygon }) {
      commit('REMOVE_POLYGON', { rule, polygon })
    },
    resetTemplate ({ commit }) {
      commit('CHANGE_TYPE', { type: null })
      commit('CHANGE_TEMPLATE', { template: { text: null } })
    },
    changePreset ({ commit, dispatch, state, rootGetters }, { type, template }) {
      const current = rootGetters.truncationRule
      if (current && type !== state.preset.type && template !== state.preset.template) {
        commit('REMOVE', current.id)
      }
      if (notEmpty(type)) {
        const types = state.templates.types.available
        const typeId = Object.keys(types).find(id => types[`${id}`].name === type)
        commit('CHANGE_TYPE', { type: typeId })
        commit('CHANGE_TEMPLATE', { template: { text: null } })
      }
      if (notEmpty(template)) {
        commit('CHANGE_TEMPLATE', { template })
        dispatch('addRuleFromTemplate')
      }
    },
    changeOrder ({ commit, getters }, { polygon, direction }) {
      const newOrder = polygon.order + direction
      const newPolygons = cloneDeep(getters.current.polygons)
      Object.values(newPolygons).find(polygon => polygon.order === newOrder).order = polygon.order
      newPolygons[`${polygon.id}`].order = newOrder
      commit('CHANGE_POLYGONS', { rule: getters.current, polygons: newPolygons })
    },
    changeAngles ({ commit }, { rule, polygon, value }) {
      commit('CHANGE_ANGLES', { rule, polygon, value })
    },
    changeProportionFactors ({ commit }, { rule, polygon, value }) {
      commit('CHANGE_PROPORTION_FACTOR', { rule, polygon, value })
    },
    changeSlantFactors ({ commit }, { rule, polygon, value }) {
      if (rule.settings.hasOwnProperty(polygon.id)) {
        commit('CHANGE_FACTORS', { rule, polygon, value })
      } else {
        throw new Error(`The ${polygon.name} polygon was not found`)
      }
    },
    async updateRealization ({ commit, dispatch, rootGetters }, rule) {
      await dispatch('facies/normalize', null, { root: true })
      const data = await api.simulateRealization(
        Object.values(rootGetters.fields)
          .map(field => field.specification),
        makeTruncationRuleSpecification(rule, rootGetters)
      )
      commit('UPDATE_REALIZATION', { rule, data: data.faciesMap })
      data.fields.forEach(async field => {
        await dispatch('gaussianRandomFields/updateSimulationData', {
          grfId: Object.values(rootGetters.fields).find(item => item.name === field.name).id,
          data: field.data,
        }, { root: true })
      })
    },
    updateFields ({ commit, rootGetters }, { rule, channel, selected }) {
      rule = rule || rootGetters.truncationRule
      const existing = rule.fields.find(item => item.channel === channel)
      let previous = null
      if (existing && existing.field !== selected) {
        previous = rule.fields.find(item => item.field === selected)
        if (previous) {
          previous = { channel: previous, field: existing.field }
        } else {
          previous = null
        }
      }
      commit('CHANGE_FIELDS', { ruleId: rule.id, channel, fieldId: selected })
      if (previous) {
        commit('CHANGE_FIELDS', { ruleId: rule.id, channel: previous.channel, fieldId: previous.field })
      }
    },
    swapFacies ({ commit }, { rule, polygons }) {
      commit('SET_FACIES', { ruleId: rule.id, polygons: swapFacies(rule, polygons) })
    },
    updateFacies ({ commit, dispatch, state, rootState }, { rule, polygon, faciesId }) {
      const polygonId = polygon.id || polygon
      commit('CHANGE_FACIES', { ruleId: rule.id || rule, polygonId, faciesId })

      if (!rootState.facies.available[`${faciesId}`].previewProbability) {
        const probability = rule.polygons[`${polygonId}`].proportion
        dispatch('facies/updateProbability', { facies: faciesId, probability }, { root: true })
      }
      dispatch('normalizeProportionFactors', { rule, faciesId })
    },
    updateBackgroundFacies ({ commit }, { rule, polygon, facies }) {
      // TODO: Use EITHER polygons, or settings
      const polygons = cloneDeep(rule.polygons)
      polygons[polygon.id].group = facies
      commit('CHANGE_POLYGONS', { rule, polygons })
    },
    updateOverlayCenter ({ commit }, { rule, polygon, value }) {
      commit('UPDATE_OVERLAY_CENTER', { rule, polygon, value })
    },
    updateOverlayFraction ({ commit }, { rule, polygon, value }) {
      commit('UPDATE_OVERLAY_FRACTION', { rule, polygon, value })
    },
    toggleOverlay ({ commit, dispatch }, { rule, value }) {
      commit('CHANGE_OVERLAY_USAGE', { rule, value })
      if (Object.values(rule.polygons).filter(({ overlay }) => !!overlay).length === 0) {
        dispatch('addPolygon', { rule, overlay: true })
      }
    },
    normalizeProportionFactors ({ dispatch, rootGetters }, { rule, faciesId }) {
      if (rule.type === 'non-cubic') {
        const assignedPolygons = Object.values(rule.polygons).filter(polygon => polygon.facies === faciesId)
        if (assignedPolygons.length > 1) {
          // The relevant facies has been assigned to multiple polygons
          if (
            assignedPolygons
              .map(polygon => rule.settings[polygon.id])
              .reduce((sum, polygon) => sum + polygon.fraction, 0) > 1
          ) {
            assignedPolygons.forEach(polygon => dispatch('changeProportionFactors', { rule, polygon, value: 1 / assignedPolygons.length }))
          }
        }
        // Ensure that facies that has only been assigned to a single polygon have a 'Proportion Factor' of 1
        rootGetters['facies/selected']
          .map(facies => Object.values(rule.polygons).filter(polygon => polygon.facies === facies.id))
          .filter(items => items.length === 1)
          .map(items => items[0])
          .map(polygon => dispatch('changeProportionFactors', { rule, polygon, value: 1 }))
      }
    },
    // TODO: refactor, so that this method signalizes it should ONLY be called
    //       when the user changes the template. NOT when changing the template (e.g. switching between zones/regions)
    //       addRuleFromTemplate ?
    addRuleFromTemplate ({ commit, dispatch, state, rootGetters }) {
      const rule = Object.values(state.templates.available).find(template => template.name === state.preset.template && template.type === state.preset.type)
      const missing = rule.minFields - Object.values(rootGetters.fields).length
      if (missing > 0) {
        for (let i = 0; i < missing; i++) dispatch('gaussianRandomFields/addEmptyField', {}, { root: true })
      }
      return dispatch('add', { ...rule, type: state.preset.type })
        .then(ruleId => {
          rule.polygons.forEach(polygon => {
            if (polygon.facies && polygon.proportion >= 0) {
              const facies = rootGetters['facies/byName'](polygon.facies)
              if (facies) {
                dispatch('facies/updateProbability', { facies, probability: polygon.proportion }, { root: true })
              } else {
                // TODO: Handle appropriately
                // throw new Error(`The facies ${polygon.facies} does not exist`)
              }
            }
          })
        })
    }
  },

  mutations: {
    ADD: (state, { id, item }) => {
      ADD_ITEM(state.rules, { id, item })
    },
    REMOVE: (state, ruleId) => {
      Vue.delete(state.rules, ruleId)
    },
    REMOVE_POLYGON: (state, { rule, polygon }) => {
      Vue.delete(state.rules[`${rule.id}`].settings, polygon.id)
      Vue.delete(state.rules[`${rule.id}`].polygons, polygon.id)
    },
    SET_FACIES: (state, { ruleId, polygons }) => {
      Vue.set(state.rules[`${ruleId}`], 'polygons', polygons)
    },
    UPDATE_REALIZATION: (state, { rule, data }) => {
      Vue.set(state.rules[`${rule.id}`], '_realization', data)
    },
    ADD_SETTING: (state, { rule, polygon, setting }) => {
      Vue.set(state.rules[`${rule.id}`].settings, polygon.id, setting)
    },
    CHANGE_OVERLAY_USAGE: (state, { rule, value }) => {
      state.rules[`${rule.id}`]._useOverlay = value
    },
    UPDATE_OVERLAY_CENTER: (state, { rule, polygon, value }) => {
      state.rules[rule.id].polygons[polygon.id].center = value
    },
    UPDATE_OVERLAY_FRACTION: (state, { rule, polygon, value }) => {
      state.rules[rule.id].polygons[polygon.id].fraction = value
    },
    CHANGE_TYPE: (state, { type }) => changePreset(state, 'type', type),
    CHANGE_TEMPLATE: (state, { template }) => changePreset(state, 'template', template.text),
    CHANGE_FACIES: (state, { ruleId, polygonId, faciesId }) => {
      state.rules[`${ruleId}`].polygons[`${polygonId}`].facies = faciesId
    },
    CHANGE_SETTINGS: (state, { rule, settings }) => {
      setProperty(state, rule, 'settings', settings)
    },
    CHANGE_POLYGONS: (state, { rule, polygons }) => {
      setProperty(state, rule, 'polygons', polygons)
    },
    CHANGE_ANGLES: (state, { rule, polygon, value }) => {
      state.rules[`${rule.id}`].settings[`${polygon.id}`].angle = value
    },
    CHANGE_FIELDS: (state, { ruleId, channel, fieldId }) => {
      state.rules[`${ruleId}`].fieldByChannel(channel).field = fieldId
    },
    CHANGE_PROPORTION_FACTOR: (state, { rule, polygon, value }) => {
      setSettingValue(state, rule, polygon, 'fraction', value)
    },
    CHANGE_FACTORS: (state, { rule, polygon, value }) => {
      setSettingValue(state, rule, polygon, 'factor', value)
    }
  },

  getters: {
    current (state, getters, rootState, rootGetters) {
      return state.rules
        ? Object.values(state.rules).find(rule => hasCurrentParents(rule, rootGetters))
        : null
    },
    ready (state) {
      return (id) => {
        const rule = id
          ? state.rules[`${id}`]
          : null
        return !!rule &&
               allSet(rule.fields, 'field') &&
               allSet(rule.polygons, 'facies')
      }
    },
    relevant (state, getters, rootState, rootGetters) {
      return Object.values(state.rules)
        .filter(rule => hasCurrentParents(rule, rootGetters) && hasEnoughFacies(rule, rootGetters))
    },
    typeById (state) {
      return (id) => {
        const rule = state.templates.types.available[`${id}`]
        return rule
          ? rule.type
          : null
      }
    },
    ruleTypes (state, getters, rootState, rootGetters) {
      return Object.values(state.templates.types.available)
        .map(rule => {
          return {
            text: rule.name,
            disabled: !hasEnoughFacies(rule, rootGetters)
          }
        })
    },
    ruleNames (state, getters, rootState, rootGetters) {
      return Object.values(state.templates.available)
        .filter(template => template.type === state.preset.type)
        .map(template => {
          return {
            text: template.name,
            disabled: !hasEnoughFacies(template, rootGetters)
          }
        })
    },
  },
}

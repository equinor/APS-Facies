import Vue from 'vue'
import { cloneDeep, isNumber } from 'lodash'
import uuidv4 from 'uuid/v4'

import api from '@/api/rms'

import templates from '@/store/modules/truncationRules/templates'

import { Bayfill, NonCubic } from '@/store/utils/domain/truncationRule'
import { ADD_ITEM } from '@/store/mutations'
import { addItem } from '@/store/actions'
import {
  hasCurrentParents,
  minFacies,
  hasEnoughFacies,
  hasParents,
  isEmpty,
  makeTruncationRuleSpecification,
  notEmpty,
  resolve,
  sortAlphabetically,
} from '@/utils'
import { getId } from '@/utils/typing'

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

const getFaciesGroup = (getters, dispatch, over, parent) => dispatch(
  'facies/groups/get', {
    facies: over.map(facies => findFaciesByIndex(getters, facies).id),
    parent
  }, { root: true }
)

const findOverlayGroup = (getters, over, parent) => {
  const facies = over.map(facies => findFaciesByIndex(getters, facies).id)
  return getters['facies/groups/byFacies'](facies, parent)
}

const processOverlay = (getters, overlay, parent) => {
  if (!overlay) return null
  const items = {}
  overlay.items.forEach(({ over, polygons }, index) => {
    polygons.forEach(({ field, facies, probability, interval }) => {
      const id = uuidv4()
      items[`${id}`] = {
        id,
        group: findOverlayGroup(getters, over, parent).id,
        field: findField(getters, field).id,
        facies: findFacies(getters, facies).id,
        fraction: probability,
        center: interval,
        order: index,
      }
    })
  })
  return { ...overlay, items }
}

const findItem = ({ findByIndex, findByName, findDefaultName = (arg) => null }) => (getters, item) => {
  let result = null
  if (item.index >= 0) {
    result = findByIndex(getters, item)
  } else if (item.name || typeof item === 'string') {
    result = findByName(getters, item)
  }
  return result || findDefaultName({ getters, item })
}

const findField = (getters, field, parent = {}) => {
  return findItem({
    findByIndex: findFieldByIndex,
    findByName: (_getters, _field) => _getters.fields.find(({ name }) => name === _field.name),
    findDefaultName: ({ item: field }) => getters.allFields
      .filter(field => hasParents(field, parent.zone, parent.region)) // TODO: Use field.isChildOf()
      .find(({ name }) => field.name === name)
  })(getters, field)
}

const findFieldByIndex = (getters, field) => {
  const relevantFields = sortAlphabetically(getters.fields)
  return relevantFields[`${field.index}`]
}

const findFacies = (getters, facies) => {
  return findItem({
    findByIndex: findFaciesByIndex,
    findByName: (_getters, _facies) => _getters['facies/selected'].find(item => item.facies === _getters.faciesTable.find(({ name }) => _facies === name).id)
  })(getters, facies)
}

const findFaciesByIndex = (getters, facies) => {
  const relevantFacies = sortAlphabetically(getters['facies/selected'])
  return relevantFacies[`${facies.index}`]
}

const processFields = (getters, state, fields, parent = {}) => {
  if (state.options.automaticAlphaFieldSelection.value) {
    return fields.map(item => {
      const field = findField(getters, item.field, parent)
      return {
        channel: item.channel,
        field: field ? field.id : null
      }
    })
  } else {
    return process(getters, fields, 'field', 'gaussianRandomField', 'field.name')
  }
}

const processPolygons = (getters, { polygons, type, settings }) => {
  const autoFill = true
  polygons = processSettings(polygons, type, settings)
  if (autoFill) {
    polygons = polygons.map(polygon => {
      const name = getters['facies/name'](findFacies(getters, polygon.facies))
      return {
        ...polygon,
        facies: name || null,
      }
    })
  }
  return process(getters, polygons, 'facies', 'facies', 'facies')
    .map(polygon => {
      return {
        ...polygon,
        facies: getters['facies/selected'].find(facies => facies.facies === getters['facies/byId'](polygon.facies).id).id,
      }
    })
}

const findPolygonInRule = (rule, polygon) => {
  return rule._polygons[`${polygon.id}`]
}

const setFacies = (polygons, src, dest) => {
  polygons[`${dest.id}`].facies = src.facies
}

function swapFacies (rule, polygons) {
  if (polygons.length !== 2) throw new Error('Only two polygons may be swapped')
  const newPolygons = cloneDeep(rule._polygons)

  const first = findPolygonInRule(rule, polygons[0])
  const other = findPolygonInRule(rule, polygons[1])

  setFacies(newPolygons, first, other)
  setFacies(newPolygons, other, first)

  return newPolygons
}

const setPolygonValue = (state, rule, polygon, property, value) => {
  Vue.set(state.rules[`${rule.id}`]._polygons[`${polygon.id}`], property, value)
}

const setProperty = (state, rule, property, values) => {
  Vue.set(state.rules[`${rule.id}`], property, values)
}

const processSetting = (type, setting) => {
  if (type === 'non-cubic') {
    setting = {
      ...setting,
      angle: {
        value: setting.angle,
        updatable: setting.updatable,
      }
    }
    delete setting.updatable
    delete setting.polygon
  }
  return setting
}

const processSettings = (polygons, type, settings) => polygons.map(polygon => {
  const setting = settings.find(setting => setting.polygon === polygon.name)
  if (setting) {
    return {
      ...processSetting(type, setting),
      ...polygon,
    }
  } else {
    return polygon
  }
})

const typeMapping = {
  'bayfill': Bayfill,
  'non-cubic': NonCubic,
  'cubic': null, // TODO
}

const makeRule = ({ type, ...rest }, _isParsed = false) => {
  if (!typeMapping.hasOwnProperty(type)) {
    throw new Error(`The truncation rule of type ${type} is not implemented`)
  }
  return new typeMapping[`${type}`]({ type, _isParsed, ...rest })
}

function compareTemplate (rootGetters, a, b) {
  const _minFacies = item => minFacies(item, rootGetters)
  if (_minFacies(a) > _minFacies(b)) {
    return +1
  } else if (_minFacies(a) < _minFacies(b)) {
    return -1
  } else {
    return a.name.localeCompare(b.name)
  }
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
    async add ({ commit, dispatch, state, rootGetters, rootState }, { type, name, polygons, overlay, fields, settings, parent }) {
      parent = parent || { zone: rootGetters.zone, region: rootGetters.region }
      type = state.templates.types.available[`${type}`].type
      const autoFill = true
      if (autoFill && overlay) {
        await Promise.all(overlay.items.map(item => getFaciesGroup(rootGetters, dispatch, item.over, parent)))
      }
      const rule = makeRule({
        type,
        polygons: processPolygons(rootGetters, { polygons, type, settings }),
        fields: processFields(rootGetters, rootState, fields, parent),
        overlay: processOverlay(rootGetters, overlay, parent),
        name,
        ...parent,
      })
      const addProportions = (proportions, polygons) => {
        if (isEmpty(polygons)) return proportions
        Object.values(polygons).forEach(({ facies, proportion }) => {
          proportions.push({ facies, probability: proportion || 1 })
        })
        return proportions
      }
      if (autoFill) {
        if (rootGetters['facies/unset']) {
          const normalize = (items) => {
            const sum = items.reduce((sum, { probability }) => sum + probability, 0)
            return items.map(payload => { return { ...payload, probability: payload.probability / sum } })
          }
          const proportions = []
          addProportions(proportions, rule.polygons)
          await Promise.all(normalize(proportions)
            .map(payload => dispatch('facies/updateProbability', payload, { root: true }))
          )
        }
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
    async populate ({ commit, dispatch }, { rules, templates, preset }) {
      if (preset.type) commit('CHANGE_TYPE', preset)
      if (preset.template) commit('CHANGE_TEMPLATE', preset)
      await dispatch('templates/populate', templates)
      return Promise.all(Object.values(rules).map(rule => {
        return addItem({ commit }, { id: rule._id, item: makeRule({ ...rule, _isParsed: true }) })
      }))
    },
    async addPolygon ({ commit, dispatch, rootState }, { rule, group = '', order = null, overlay = false }) {
      if (group) group = getId(group)
      if (!isNumber(order) || order < 0) {
        const polygons = rule.polygons
        // TODO: Filter on group as well
          .filter(polygon => polygon.overlay === overlay)
        order = polygons.length === 0
          ? 0
          : 1 + polygons
            .map(polygon => polygon.order)
            .reduce((max, curr) => curr > max ? curr : max, 0)
      }
      // TODO: Make polygon into a proper class
      const polygon = {
        id: uuidv4(),
        overlay,
        facies: '',
        fraction: 1,
        proportion: 1, // TODO: ...
        order,
        name: 1 + rule.polygons
          .map(polygon => polygon.name)
          .reduce((max, curr) => curr > max ? curr : max, 0),
      }
      if (overlay) {
        let field = ''
        if (
          (
            rule.overlayPolygons
              .filter(polygon => polygon.group === group).length + 1
          ) > (Object.values(rootState.gaussianRandomFields.fields).length - rule.backgroundFields.length)
        ) {
          field = await dispatch('gaussianRandomFields/addEmptyField', { ...rule.parent }, { root: true })
        }
        polygon.center = 0
        polygon.field = field
        polygon.group = group
      }
      if (rule.type === 'bayfill') {
        throw new Error('Bayfill must have exactly 5 polygons. Cannot add more.')
      } else if (rule.type === 'non-cubic') {
        if (!overlay) {
          polygon.angle = {
            value: 0,
            updatable: false,
          }
        }
      } else if (rule.type === 'cubic') {
        throw new Error('Cubic is not implemented')
      }
      const polygons = cloneDeep(rule._polygons)
      Object.values(polygons).forEach(polygon => {
        if (polygon.order >= order && polygon.overlay === overlay) {
          polygon.order += 1
        }
      })
      polygons[polygon.id] = polygon
      commit('CHANGE_POLYGONS', { rule, polygons })
    },
    async removePolygon ({ commit, dispatch, rootState }, { rule, polygon }) {
      commit('REMOVE_POLYGON', { rule, polygon })

      // Remove from facies group (if it is no longer a background facies)
      if (!rule.backgroundPolygons.map(({ facies }) => facies).includes(polygon.facies)) {
        const group = Object.values(rootState.facies.groups.available).find(group => group.facies.includes(polygon.facies))
        const facies = group.facies.filter(facies => facies !== polygon.facies)
        if (facies.length > 0) {
          await dispatch('facies/groups/update', { group, facies }, { root: true })
        } else {
          rule.overlayPolygons
            .filter(polygon => polygon.group === getId(group))
            .forEach(polygon => {
              commit('REMOVE_POLYGON', { rule, polygon })
            })
          await dispatch('facies/groups/remove', group, { root: true })
        }
      }

      // Remove lingering Facies Group (if overlay)
      if (polygon.overlay) {
        const group = rootState.facies.groups.available[`${polygon.group}`]
        if (rule.overlayPolygons.filter(polygon => polygon.group === group.id).length === 0) {
          await dispatch('facies/groups/remove', group, { root: true })
        }
      }
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
      commit('CHANGE_FACTORS', { rule, polygon, value })
    },
    async updateRealization ({ commit, dispatch, rootGetters }, rule) {
      await dispatch('facies/normalize', null, { root: true })
      const data = await api.simulateRealization(
        Object.values(rootGetters.fields)
          .map(field => field.specification({ rootGetters })),
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
    deleteField ({ commit, dispatch, state }, { grfId }) {
      return Promise.all(
        Object.values(state.rules)
          .filter(rule => !!rule.fields.some(({ field }) => field === grfId))
          .map(rule => dispatch('updateFields', {
            rule,
            channel: rule.fields.find(({ field }) => field === grfId).channel,
            selected: null
          }))
      )
    },
    updateFields ({ commit, rootGetters }, { rule, channel, selected = '' }) {
      // TODO: Use POLYGONS instead of channels
      rule = rule || rootGetters.truncationRule
      const existing = rule.fields.find(item => item.channel === channel)
      let previous = null
      if (existing && existing.field !== selected) {
        previous = rule.fields.find(item => item.field === selected)
        if (previous && isNumber(previous.channel)) {
          previous.field = existing.field
        } else if (previous) {
          previous = {
            channel: previous,
            field: existing.field,
            overlay: (previous > 3 && rule instanceof Bayfill) || (previous > 2 && !(rule instanceof Bayfill)),
          }
        } else {
          previous = null
        }
      }
      commit('CHANGE_FIELDS', { ruleId: rule.id, channel, fieldId: selected })
      if (previous && !previous.overlay && previous.channel.field) {
        commit('CHANGE_FIELDS', { ruleId: rule.id, channel: previous.channel, fieldId: previous.field })
      }
    },
    swapFacies ({ commit }, { rule, polygons }) {
      commit('SET_FACIES', { ruleId: rule.id, polygons: swapFacies(rule, polygons) })
    },
    async updateFacies ({ commit, dispatch, state, rootState }, { rule, polygon, faciesId }) {
      const polygonId = polygon.id || polygon
      commit('CHANGE_FACIES', { ruleId: rule.id || rule, polygonId, faciesId })

      if (!rootState.facies.available[`${faciesId}`].previewProbability) {
        const probability = rule._polygons[`${polygonId}`].proportion
        await dispatch('facies/updateProbability', { facies: faciesId, probability }, { root: true })
      }
      await dispatch('normalizeProportionFactors', { rule })
    },
    updateBackgroundGroup ({ commit }, { rule, polygon, group }) {
      commit('UPDATE_BACKGROUND_GROUP', { rule, polygon, value: group })
    },
    update ({ commit }, { rule, polygon, facies }) {
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
    toggleOverlay ({ commit }, { rule, value }) {
      commit('CHANGE_OVERLAY_USAGE', { rule, value })
    },
    async normalizeProportionFactors ({ dispatch, rootGetters }, { rule }) {
      const proportional = false /* TODO: should be moved to the state as an option for the user */
      const facies = rule.polygons
        .reduce((obj, polygon) => {
          const id = polygon.facies
          if (id) {
            if (!obj.hasOwnProperty(id)) obj[`${id}`] = []
            obj[`${id}`].push(polygon)
          }
          return obj
        }, {})
      await Promise.all(Object.values(facies)
        .map(polygons => {
          const sum = polygons.reduce((sum, polygon) => sum + polygon.fraction, 0)
          return sum !== 1
            ? Promise.all(polygons.map(polygon => dispatch('changeProportionFactors', {
              rule,
              polygon,
              value: isNumber(polygon.fraction) && polygon.fraction > 0 && proportional
                ? polygon.fraction / sum
                : 1 / polygons.length,
            })))
            : new Promise((resolve, reject) => resolve(null))
        })
      )

      // Ensure that facies that has only been assigned to a single polygon have a 'Proportion Factor' of 1
      await Promise.all(rootGetters['facies/selected']
        .map(facies => rule.polygons.filter(polygon => polygon.facies === facies.id))
        .filter(items => items.length === 1)
        .map(items => items[0])
        .map(polygon => dispatch('changeProportionFactors', { rule, polygon, value: 1 })))
    },
    // TODO: refactor, so that this method signalizes it should ONLY be called
    //       when the user changes the template. NOT when changing the template (e.g. switching between zones/regions)
    //       addRuleFromTemplate ?
    async addRuleFromTemplate ({ commit, dispatch, state, rootGetters }) {
      const rule = Object.values(state.templates.available).find(template => template.name === state.preset.template && template.type === state.preset.type)
      const missing = rule.minFields - Object.values(rootGetters.fields).length
      if (missing > 0) {
        for (let i = 0; i < missing; i++) dispatch('gaussianRandomFields/addEmptyField', {}, { root: true })
      }
      // TODO: Add overlay groups
      await dispatch('add', { ...rule, type: state.preset.type })
      await Promise.all(rule.polygons.map(polygon => {
        if (polygon.facies && polygon.proportion >= 0) {
          const facies = rootGetters['facies/byName'](polygon.facies)
          if (facies) {
            dispatch('facies/updateProbability', { facies, probability: polygon.proportion }, { root: true })
          } else {
            // TODO: Handle appropriately
            // throw new Error(`The facies ${polygon.facies} does not exist`)
          }
        }
      }))
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
      Vue.delete(state.rules[`${rule.id}`]._polygons, polygon.id)
    },
    SET_FACIES: (state, { ruleId, polygons }) => {
      Vue.set(state.rules[`${ruleId}`], '_polygons', polygons)
    },
    UPDATE_REALIZATION: (state, { rule, data }) => {
      Vue.set(state.rules[`${rule.id}`], '_realization', data)
    },
    CHANGE_OVERLAY_USAGE: (state, { rule, value }) => {
      state.rules[`${rule.id}`]._useOverlay = value
    },
    UPDATE_OVERLAY_CENTER: (state, { rule, polygon, value }) => {
      state.rules[rule.id]._polygons[polygon.id].center = value
    },
    UPDATE_OVERLAY_FRACTION: (state, { rule, polygon, value }) => {
      state.rules[rule.id]._polygons[polygon.id].fraction = value
    },
    UPDATE_BACKGROUND_GROUP: (state, { rule, polygon, value }) => {
      state.rules[rule.id]._polygons[polygon.id].group = value
    },
    CHANGE_TYPE: (state, { type }) => changePreset(state, 'type', type),
    CHANGE_TEMPLATE: (state, { template }) => changePreset(state, 'template', template.text),
    CHANGE_FACIES: (state, { ruleId, polygonId, faciesId }) => {
      state.rules[`${ruleId}`]._polygons[`${polygonId}`].facies = faciesId
    },
    CHANGE_POLYGONS: (state, { rule, polygons }) => {
      setProperty(state, rule, '_polygons', polygons)
    },
    CHANGE_ANGLES: (state, { rule, polygon, value }) => {
      Vue.set(state.rules[`${rule.id}`]._polygons[`${polygon.id}`], 'angle', value)
    },
    CHANGE_FIELDS: (state, { ruleId, channel, fieldId }) => {
      state.rules[`${ruleId}`].fieldByChannel(channel).field = fieldId
    },
    CHANGE_PROPORTION_FACTOR: (state, { rule, polygon, value }) => {
      setPolygonValue(state, rule, polygon, 'fraction', value)
    },
    CHANGE_FACTORS: (state, { rule, polygon, value }) => {
      setPolygonValue(state, rule, polygon, 'factor', value)
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
        return !!rule && rule.ready
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
        .sort((a, b) => compareTemplate(rootGetters, a, b))
        .map(template => {
          return {
            text: template.name,
            disabled: !hasEnoughFacies(template, rootGetters)
          }
        })
    },
  },
}

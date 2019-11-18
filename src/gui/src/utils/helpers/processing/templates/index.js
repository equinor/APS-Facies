import uuidv4 from 'uuid/v4'

import {
  getId,
  hasParents,
  resolve,
  sortAlphabetically,
  sortByProperty,
} from '@/utils'
import {
  Bayfill,
  NonCubic,
  Cubic,
} from '@/utils/domain'
import { makePolygonsFromSpecification } from './typed'

const processSetting = (type, setting) => {
  if (type === 'non-cubic') {
    setting = {
      ...setting,
      angle: {
        value: setting.angle,
        updatable: setting.updatable,
      },
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

const process = (getters, items, target, type, path) => {
  return items.map(item => {
    const updated = {
      ...item,
    }
    updated[`${target}`] = getters.id(type, resolve(path, item))
    return updated
  })
}

export function processFields ({ rootGetters, rootState }, fields, parent = {}) {
  if (rootState.options.automaticAlphaFieldSelection.value) {
    return fields
      .map(item => {
        const field = findField(rootGetters, item.field, parent)
        return {
          channel: item.channel,
          field: field || null
        }
      })
      .sort((a, b) => a.channel - b.channel)
      .map(({ field }) => field)
  } else {
    return process(rootGetters, fields, 'field', 'gaussianRandomField', 'field.name')
  }
}

const findOverlayGroup = (getters, over, parent) => {
  const facies = over.map(facies => findFaciesByIndex(getters, facies).id)
  return getters['facies/groups/byFacies'](facies, parent)
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

const typeMapping = {
  'bayfill': Bayfill,
  'non-cubic': NonCubic,
  'cubic': Cubic,
}

export function makeRule ({ type, ...rest }) {
  if (!typeMapping.hasOwnProperty(type)) {
    throw new Error(`The truncation rule of type ${type} is not implemented`)
  }
  return new typeMapping[`${type}`]({ type, ...rest })
}

export function getFaciesGroup ({ rootGetters, dispatch }, over, parent) {
  return dispatch(
    'facies/groups/get', {
      facies: over.map(facies => findFaciesByIndex(rootGetters, facies)),
      parent
    }, { root: true }
  )
}

export function combinePolygons (polygons, overlay, _isParsed = false) {
  const combination = []
  const add = (item, overlay = false) => {
    combination.push({ ...item, overlay })
  }
  if (_isParsed) {
    return polygons
  } else {
    if (overlay && overlay.items) overlay = overlay.items
    Object.values(polygons).forEach(polygon => add(polygon, false))
    if (overlay) {
      sortByProperty('order')(overlay).forEach(polygon => add(polygon, true))
    }
    return combination
  }
}

export function structurePolygons (polygons) {
  return polygons.map((polygon, index) => {
    if (polygon.level) {
      /* I.E. Dealing with cubic polygons */
      return {
        ...polygon,
        order: polygon.level.reduce((order, level, index) => {
          if (level > 0) {
            order += (level - 1 /* 1-indexed */) * (index + 1 /* 0-indexed */)
          }
          return order
        }, 0)
      }
    } else {
      return {
        ...polygon,
        order: index,
      }
    }
  })
}

const findField = (getters, field, parent = {}) => {
  return findItem({
    findByIndex: findFieldByIndex,
    findByName: (_getters, _field) => _getters.fields.find(({ name }) => name === _field.name),
    findDefaultName: ({ item: field }) => getters.allFields
      .filter(field => hasParents(field, parent.zone, parent.region)) // TODO: Use field.isChildOf()
      .find(({ name }) => field.name === name),
  })(getters, field)
}

const findFieldByIndex = (getters, field) => {
  const relevantFields = sortAlphabetically(getters.fields)
  return relevantFields[`${field.index}`]
}
const findFacies = (getters, facies) => {
  return findItem({
    findByIndex: findFaciesByIndex,
    findByName: (_getters, _facies) => {
      return _getters['facies/selected']
        .find(item => item.facies === _getters.faciesTable.find(({ name }) => _facies === name).id)
    },
  })(getters, facies)
}

export function processOverlay ({ rootGetters }, overlay, parent) {
  if (!overlay) return null
  const items = {}
  overlay.items.forEach(({ over, polygons }, index) => {
    polygons.forEach(({ field, facies, probability, interval }) => {
      const id = uuidv4()
      items[`${id}`] = {
        id,
        group: findOverlayGroup(rootGetters, over, parent),
        field: findField(rootGetters, field),
        facies: findFacies(rootGetters, facies),
        fraction: probability,
        center: interval,
        order: index,
      }
    })
  })
  return { ...overlay, items }
}
export function processPolygons ({ rootGetters, rootState }, { polygons, type, settings }) {
  const autoFill = rootState.options.automaticFaciesFill.value
  polygons = processSettings(polygons, type, settings)
  if (autoFill) {
    polygons = polygons.map(polygon => {
      const name = rootGetters['facies/name'](findFacies(rootGetters, polygon.facies))
      return {
        ...polygon,
        facies: name || null,
      }
    })
  }
  return process(rootGetters, polygons, 'facies', 'facies', 'facies')
    .map(polygon => {
      return {
        ...polygon,
        facies: rootGetters['facies/selected']
          .find(facies => getId(facies.facies) === getId(rootGetters['facies/byId'](polygon.facies))),
      }
    })
}

export function findFaciesByIndex (getters, facies) {
  const relevantFacies = sortAlphabetically(getters['facies/selected'])
  return relevantFacies[`${facies.index}`]
}

export { makePolygonsFromSpecification }

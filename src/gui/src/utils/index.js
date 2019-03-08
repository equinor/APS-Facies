import _ from 'lodash'
import uuidv5 from 'uuid/v5'
import { getId } from '@/utils/typing'

const makeData = (items, _class, originals = null) => {
  originals = originals ? Object.values(originals) : []
  const data = {}
  if (_class.toLocaleString().indexOf('"CodeName"') >= 0 || _class.toLocaleString().indexOf('"Named"') >= 0) {
    items = items.filter(({ name }) => !!name)
  }
  for (const item of items) {
    const instance = originals
      .find(original => Object.keys(item)
        .every(key => original[`${key}`] === item[`${key}`])
      ) || new _class(item)
    data[instance.id] = instance
  }
  return data
}

const defaultSimulationSettings = () => {
  return {
    gridAzimuth: 0,
    gridSize: { x: 100, y: 100, z: 1 },
    simulationBox: { x: 1000, y: 1000, z: 10 },
    simulationBoxOrigin: { x: 0, y: 0 },
  }
}

const makeTruncationRuleSpecification = (rule, rootGetters) => {
  return {
    type: rule.type,
    globalFaciesTable: rootGetters['facies/selected']
      .filter(facies => rootGetters.options.filterZeroProbability ? facies.previewProbability && facies.previewProbability > 0 : true)
      .map(({ facies, previewProbability, id }) => {
        let polygon = rule.polygons.find(polygon => polygon.facies === id)
        if (isEmpty(polygon) && rule.overlay) {
          polygon = Object.values(rule.overlay).find(polygon => polygon.facies === id)
        }
        const globalFacies = rootGetters.faciesTable.find(({ id }) => id === facies)
        return {
          code: globalFacies.code,
          name: globalFacies.name,
          probability: previewProbability,
          inZone: true,
          inRule: Object.is(polygon, undefined) ? -1 : polygon.order,
        }
      }),
    gaussianRandomFields: Object.values(rootGetters.fields)
      .map(field => {
        const alpha = rule.fields.find(item => item.field === field.id)
        return {
          name: field.name,
          inZone: true,
          inRule: rule.fields.findIndex(item => item.field === field.id),
          inBackground: alpha
            ? !alpha.overlay
            : true,
        }
      }),
    values: rule.specification({ rootGetters }),
    constantParameters: !rootGetters.faciesTable.some(facies => !!facies.probabilityCube),
  }
}

const hasFaciesSpecifiedForMultiplePolygons = (polygons, facies = null) => {
  if (polygons instanceof Object) polygons = Object.values(polygons)
  if (!polygons || polygons.length === 0) return false
  const faciesCount = polygons
    .filter(polygon => facies ? polygon.facies === facies : true)
    .reduce((counts, { facies }) => {
      counts.hasOwnProperty(facies)
        ? counts[`${facies}`] += 1
        : counts[`${facies}`] = 1
      return counts
    }, {})
  return Object.values(faciesCount).some(count => count > 1)
}

function selectItems ({ items, state, _class }) {
  const ids = items.map(item => item.id || item._id)
  const obj = {}
  for (const id in state.available) {
    const item = state.available[`${id}`]
    obj[`${id}`] = new _class({
      _id: id,
      ...item,
      selected: ids.indexOf(id) >= 0
    })
  }
  return obj
}

// TODO: reuse / generalize `hasValidChildren`
const invalidateChildren = component => {
  let children = component.$children.slice()
  while (children.length > 0) {
    const child = children.shift()
    if (typeof child !== 'undefined' && child.dialog !== false) {
      if (child.$v && child.$v.$invalid) {
        child.$v.$touch()
      }
      children = children.concat(child.$children.slice())
    }
  }
}

const hasValidChildren = component => {
  let children = component.$children.slice()
  while (children.length > 0) {
    const child = children.shift()
    if (typeof child !== 'undefined' && child.dialog !== false) {
      if (child.$v && child.$v.$invalid) {
        return false
      }
      children = children.concat(child.$children.slice())
    }
  }
  return true
}

const hasCurrentParents = (item, getters) => {
  return !!getters && getters.zone
    ? hasParents(item, getters.zone, getters.region)
    : false
}

const hasParents = (item, zone, region) => {
  if (item.parent.zone === getId(zone)) {
    // The Zone ID is consistent
    if (region) {
      // We are dealing with a 'thing', that is SUPPOSED to have a region
      return item.parent.region === getId(region)
    } else {
      // The 'thing' should NOT have a region
      return !item.parent.region
    }
  } else {
    return false
  }
}

const parentId = ({ zone, region }) => {
  if (region) {
    return uuidv5(getId(region), getId(zone))
  } else {
    return getId(zone)
  }
}

const faciesName = obj => {
  if (obj.hasOwnProperty('facies')) obj = obj.facies
  if (obj.hasOwnProperty('name')) obj = obj.name
  return obj
}

const availableForBackgroundFacies = (getters, rule, facies) => {
  return !(
    getters['facies/groups/used'](facies) ||
    rule.overlayPolygons.map(({ facies }) => facies).indexOf(getId(facies)) >= 0
  )
}

const minFacies = (rule, getters) => {
  let minFacies = 0
  const type = getters['truncationRules/typeById'](rule.type) || rule.type
  switch (type) {
    case 'cubic':
      // TODO: Implement
      minFacies = Number.POSITIVE_INFINITY
      break
    case 'non-cubic':
      if (rule.polygons) {
        const uniqueFacies = new Set(rule.polygons.map(polygon => faciesName(polygon)))
        if (rule.overlay) {
          const items = Object.values(rule.overlay.items || rule.overlay)
          items.forEach(item => {
            item.polygons
              ? item.polygons.forEach(polygon => {
                uniqueFacies.add(polygon.facies.name)
              })
              : uniqueFacies.add(item.facies)
          })
        }
        minFacies = uniqueFacies.size
      } else {
        minFacies = 2
      }
      break
    case 'bayfill':
      minFacies = 5
      break
    default:
      throw new Error(`${type} is not implemented`)
  }
  return minFacies
}

const hasEnoughFacies = (rule, getters) => {
  const numFacies = getters['facies/selected'].length
  return numFacies >= minFacies(rule, getters)
}

const isEmpty = property => _.isEmpty(property)
const notEmpty = property => !isEmpty(property)

const getRandomInt = max => Math.floor(Math.random() * max)

const newSeed = () => getRandomInt(Math.pow(2, 64) - 1)

const resolve = (path, obj = self, separator = '.') => {
  const properties = Array.isArray(path) ? path : path.split(separator)
  return properties.reduce((prev, curr) => prev && prev[`${curr}`], obj)
}

const allSet = (items, prop) => {
  return items
    ? Object.values(items).every(item => !!item[`${prop}`])
    : false
}

const sortAlphabetically = arr => {
  return Object.values(arr).sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)
}

const sortByProperty = (prop) => (items) => {
  if (items instanceof Object) items = Object.values(items)
  items.forEach(item => {
    if (!item.hasOwnProperty(prop)) {
      throw new Error(`The item (${item}) does not have the required property on which to sort (${prop})`)
    }
  })
  return items.slice().sort((polygon, other) => polygon[`${prop}`] - other[`${prop}`])
}

const sortByOrder = (items, index, isDescending) => {
  // Used in Vuetify's tables
  return sortByProperty('order')(items)
}

export {
  sortByProperty,
  sortByOrder,
  defaultSimulationSettings,
  makeData,
  makeTruncationRuleSpecification,
  hasFaciesSpecifiedForMultiplePolygons,
  availableForBackgroundFacies,
  selectItems,
  hasValidChildren,
  invalidateChildren,
  hasCurrentParents,
  hasParents,
  parentId,
  minFacies,
  hasEnoughFacies,
  getRandomInt,
  newSeed,
  allSet,
  resolve,
  isEmpty,
  notEmpty,
  sortAlphabetically,
}

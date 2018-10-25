import _ from 'lodash'

const makeData = (items, _class) => {
  const data = {}
  for (const item of items) {
    const instance = new _class(item)
    data[instance.id] = instance
  }
  return data
}

const makeTruncationRuleSpecification = (rule, rootGetters) => {
  return {
    type: rule.type,
    globalFaciesTable: rootGetters['facies/selected']
      .filter(facies => facies.previewProbability && facies.previewProbability > 0)
      .map(facies => {
        let polygon = Object.values(rule.polygons).find(polygon => polygon.facies === facies.id)
        if (isEmpty(polygon) && rule.overlay) {
          polygon = Object.values(rule.overlay).find(polygon => polygon.facies === facies.id)
        }
        return {
          code: facies.code,
          name: facies.name,
          probability: facies.previewProbability,
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

function selectItems ({ items, state, _class }) {
  const ids = items.map(item => item.id)
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
        child.$touch()
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
  const id = item => item.id || item

  if (item.parent.zone === id(zone)) {
    // The Zone ID is consistent
    if (region) {
      // We are dealing with a 'thing', that is SUPPOSED to have a region
      return item.parent.region === id(region)
    } else {
      // The 'thing' should NOT have a region
      return !item.parent.region
    }
  } else {
    return false
  }
}

const hasEnoughFacies = (rule, getters) => {
  let minFacies = 0
  const type = getters['truncationRules/typeById'](rule.type) || rule.type
  switch (type) {
    case 'cubic':
      // TODO: Implement
      minFacies = Number.POSITIVE_INFINITY
      break
    case 'non-cubic':
      if (rule.polygons) {
        const uniqueFacies = new Set(Object.values(rule.polygons).map(polygon => polygon.facies))
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

  const numFacies = getters['facies/selected'].length
  return numFacies >= minFacies
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

export {
  makeData,
  makeTruncationRuleSpecification,
  selectItems,
  hasValidChildren,
  invalidateChildren,
  hasCurrentParents,
  hasParents,
  hasEnoughFacies,
  getRandomInt,
  newSeed,
  allSet,
  resolve,
  isEmpty,
  notEmpty
}

const makeData = (items, _class) => {
  const data = {}
  for (const item of items) {
    const instance = new _class(item)
    data[instance.id] = instance
  }
  return data
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
  return item.parent.zone === getters.zone.id && item.parent.region ? item.parent.region === getters.region.id : true
}

const hasEnoughFacies = (rule, getters) => {
  let minFacies = 0
  switch (rule.type) {
    case 'cubic':
      // TODO: Implement
      minFacies = Number.POSITIVE_INFINITY
      break
    case 'non-cubic':
      // TODO: Implement
      minFacies = Number.POSITIVE_INFINITY
      break
    case 'bayfill':
      minFacies = 5
      break
    default:
      throw new Error(`${rule.type} is not implemented`)
  }

  const numFacies = getters['facies/selected'].length
  return numFacies >= minFacies
}

const isEmpty = property => (typeof property === 'undefined' || property === null || property === '')
const notEmpty = property => !isEmpty(property)

const getRandomInt = max => Math.floor(Math.random() * max)

const newSeed = () => getRandomInt(Math.pow(2, 64) - 1)

const resolve = (path, obj = self, separator = '.') => {
  const properties = Array.isArray(path) ? path : path.split(separator)
  return properties.reduce((prev, curr) => prev && prev[`${curr}`], obj)
}

export {
  makeData,
  selectItems,
  hasValidChildren,
  hasCurrentParents,
  hasEnoughFacies,
  getRandomInt,
  newSeed,
  resolve,
  isEmpty,
  notEmpty
}

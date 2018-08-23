const makeData = (items, _class) => {
  const data = {}
  for (const item of items) {
    const instance = new _class(item)
    data[instance.id] = instance
  }
  return data
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

const isEmpty = property => (typeof property === 'undefined' || property === null || property === '')
const notEmpty = property => !isEmpty(property)

const getRandomInt = max => Math.floor(Math.random() * max)

const newSeed = () => getRandomInt(Math.pow(2, 64) - 1)

export {
  makeData,
  hasValidChildren,
  getRandomInt,
  newSeed,
  isEmpty,
  notEmpty
}

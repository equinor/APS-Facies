const hasValidChildren = component => {
  // FIXME: The copying of array may potentially be a bottleneck
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

const notEmpty = property => !(typeof property === 'undefined' || property === null || property === '')

const getRandomInt = max => Math.floor(Math.random() * max)

const newSeed = () => getRandomInt(Math.pow(2, 64) - 1)

export {
  hasValidChildren,
  getRandomInt,
  newSeed,
  notEmpty
}

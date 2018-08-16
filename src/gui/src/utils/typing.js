import VueTypes from 'vue-types'

const rawDataType = VueTypes.arrayOf(VueTypes.object).isRequired

const nullableNumber = VueTypes.oneOfType([VueTypes.number, null]).def(null)
const nullableString = VueTypes.oneOfType([VueTypes.string, null]).def(null)
const updatableValue = {
  value: nullableNumber,
  updatable: VueTypes.bool.def(false),
}
const updatableType = VueTypes.shape({...updatableValue})
const updatableStacking = VueTypes.shape({
  ...updatableValue,
  direction: VueTypes.oneOfType([VueTypes.oneOf([-1, 1]), null]),
})

export {
  rawDataType,
  updatableType,
  updatableStacking,
  nullableString,
  nullableNumber,
}

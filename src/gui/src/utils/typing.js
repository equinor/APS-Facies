import VueTypes from 'vue-types'
import { GaussianRandomField, TruncationRule } from '@/store/utils/domain'

const rawDataType = VueTypes.arrayOf(VueTypes.object).isRequired

const nullableNumber = VueTypes.oneOfType([VueTypes.number, null]).def(null)
const nullableString = VueTypes.oneOfType([VueTypes.string, null]).def(null)
const updatableValue = {
  value: nullableNumber,
  updatable: VueTypes.bool.def(false),
}
const updatableType = VueTypes.shape({ ...updatableValue })
const updatableStacking = VueTypes.shape({
  ...updatableValue,
  direction: VueTypes.oneOfType([VueTypes.oneOf([-1, 1]), null]),
})

const hex = '[0-9a-f]'
const isUUID = value => {
  const uuid = `${hex}{8}(-${hex}{4}){3}-${hex}{8}`

  return RegExp(uuid).test(value)
}

const getId = item => {
  if (isUUID(item)) return item
  if (item && isUUID(item.id)) return item.id
  return ''
}

const _isValidId = value => {
  return typeof value === 'string' && (
    value === '' || isUUID(value)
  )
}

const _isValidIds = value => {
  return Array.isArray(value) && (
    value.length === 0 || value.every(val => _isValidId(val))
  )
}

const _isValidColor = value => {
  return RegExp(`#?${hex}{6}`).test(value) ||
    VueTypes.oneOf(['primary', 'secondary', 'accent', 'error', 'info', 'success', 'warning']) || // Vuetify aliases
    VueTypes.oneOf([]) || // Named colors
    !value // Empty string
}

const AppTypes = {
  id: VueTypes.custom(_isValidId).def(''),
  ids: VueTypes.custom(_isValidIds).def(['']),
  color: VueTypes.custom(_isValidColor),
  name: VueTypes.string,
  truncationRule: VueTypes.instanceOf(TruncationRule),
  gaussianRandomField: VueTypes.instanceOf(GaussianRandomField),
}

export {
  isUUID,
  getId,
  rawDataType,
  updatableType,
  updatableStacking,
  nullableString,
  nullableNumber,
  AppTypes,
}

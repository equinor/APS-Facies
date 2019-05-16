import VueTypes from 'vue-types'

import { Bayfill, Facies, GaussianRandomField, GlobalFacies, NonCubic } from '@/utils/domain'
import { FaciesGroup } from '@/utils/domain/facies'
import { hex, isUUID } from '@/utils/helpers'

type Optional<T> = T | null

// @ts-ignore
const nullableNumber = VueTypes.oneOfType([VueTypes.number, null]).def(null)
// @ts-ignore
const updatableValue = {
  updatable: VueTypes.bool.def(false),
  value: nullableNumber,
}
const updatableType = VueTypes.shape({ ...updatableValue })

function _isValidId (value: any): boolean {
  return typeof value === 'string'
    && (value === '' || isUUID(value))
}

function _isValidIds (value: any): boolean {
  return Array.isArray(value)
    && (value.length === 0 || value.every(val => _isValidId(val)))
}

function _isValidColor (value: any): boolean {
  return (
    RegExp(`#?${hex}{6}`).test(value)
    || VueTypes.oneOf(['primary', 'secondary', 'accent', 'error', 'info', 'success', 'warning']) // Vuetify aliases
    || VueTypes.oneOf([]) // Named colors
    || !value // Empty string
  ) as boolean
}

const AppTypes = {
  color: VueTypes.custom(_isValidColor).def(''),
  facies: VueTypes.oneOfType([
    VueTypes.instanceOf(Facies),
    VueTypes.instanceOf(FaciesGroup),
    VueTypes.instanceOf(GlobalFacies),
  ]),
  faciesGroup: VueTypes.instanceOf(FaciesGroup),
  gaussianRandomField: VueTypes.instanceOf(GaussianRandomField),
  id: VueTypes.custom(_isValidId).def(''),
  ids: VueTypes.custom(_isValidIds).def(['']),
  name: VueTypes.string,
  truncationRule: VueTypes.oneOfType([
    VueTypes.instanceOf(Bayfill),
    VueTypes.instanceOf(NonCubic),
  ]),
}

export {
  Optional,
  updatableType,
  nullableNumber,
  AppTypes,
}

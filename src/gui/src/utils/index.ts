import { Identifiable, Named, Parent } from '@/utils/domain/bases/interfaces'
import Polygon from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'
import { ID, Identified } from '@/utils/domain/types'
import {
  getId,
  newSeed,
  getRandomInt,
  isEmpty,
  notEmpty,
  allSet,
} from '@/utils/helpers'
import { hasParents } from '@/utils/domain/bases/zoneRegionDependent'
import { RootGetters } from '@/utils/helpers/store/typing'

import uuidv5 from 'uuid/v5'

interface Newable<T> { new (...args: any[]): T }

function makeData<T extends Identifiable, Y extends Identifiable> (items: T[], _class: Newable<Y>, originals: T[] | null = null): Identified<Y> {
  if (items.length === 0) return {}
  originals = originals ? Object.values(originals) : []
  const data = {}
  for (const item of items) {
    const instance = originals
      .find(original => Object.keys(item)
        .every(key => original[`${key}`] === item[`${key}`])
      ) || new _class(item)
    data[instance.id] = instance
  }
  return data
}

function defaultSimulationSettings () {
  return {
    gridAzimuth: 0,
    gridSize: { x: 100, y: 100, z: 1 },
    simulationBox: { x: 1000, y: 1000, z: 10 },
    simulationBoxOrigin: { x: 0, y: 0 },
  }
}

function makeTruncationRuleSpecification (rule: TruncationRule<Polygon>, rootGetters: RootGetters) {
  return {
    type: rule.type,
    globalFaciesTable: rootGetters['facies/selected']
      .filter((facies): boolean => rootGetters.options.filterZeroProbability ? !!facies.previewProbability && facies.previewProbability > 0 : true)
      .map(({ facies: globalFacies, previewProbability, id }) => {
        let polygon = rule.polygons.find((polygon): boolean => getId(polygon.facies) === id)
        // @ts-ignore
        if (isEmpty(polygon) && rule.overlay) {
          // @ts-ignore
          polygon = Object.values(rule.overlay).find((polygon): boolean => polygon.facies.id === id)
        }
        return {
          code: globalFacies.code,
          name: globalFacies.name,
          probability: previewProbability,
          inZone: true,
          // @ts-ignore
          inRule: Object.is(polygon, undefined) ? -1 : polygon.order,
        }
      }),
    gaussianRandomFields: Object.values(rootGetters.fields)
      .map(field => {
        return {
          name: field.name,
          inZone: true,
          inRule: rule.fields.findIndex((item): boolean => item.id === field.id),
          inBackground: rule.isUsedInBackground(field),
        }
      }),
    values: rule.specification,
    constantParameters: !rootGetters.faciesTable.some((facies): boolean => !!facies.probabilityCube),
  }
}

// @ts-ignore
function selectItems ({ items, state, _class }) {
  // @ts-ignore
  const ids = items.map(item => item.id || item._id)
  const obj = {}
  for (const id in state.available) {
    const item = state.available[`${id}`]
    obj[`${id}`] = new _class({
      _id: id,
      ...item,
      selected: ids.indexOf(id) >= 0,
    })
  }
  return obj
}

// TODO: reuse / generalize `hasValidChildren`
// @ts-ignore
function invalidateChildren (component): void {
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

// @ts-ignore
function hasValidChildren (component): boolean {
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

// @ts-ignore
function hasCurrentParents (item: any, getters): boolean {
  return !!getters && getters.zone
    ? hasParents(item, getters.zone, getters.region)
    : false
}

function parentId ({ zone, region }: Parent): ID {
  if (region) {
    return uuidv5(getId(region), getId(zone))
  } else {
    return getId(zone)
  }
}

function faciesName (obj: any) {
  if (obj.hasOwnProperty('facies')) obj = obj.facies
  if (obj.hasOwnProperty('name')) obj = obj.name
  return obj
}

function minFacies (rule: any, getters: RootGetters): number {
  let minFacies = 0
  const type = getters['truncationRules/typeById'](rule.type) || rule.type
  if (type === 'cubic') {
    // TODO: Implement
    minFacies = Number.POSITIVE_INFINITY
  } else if ([type, rule.type].includes('non-cubic')) {
    if (rule.polygons) {
      // @ts-ignore
      const uniqueFacies = new Set(rule.polygons.map(polygon => faciesName(polygon)))
      if (rule.overlay) {
        const items = Object.values(rule.overlay.items || rule.overlay)
        items.forEach(item => {
          // @ts-ignore
          item.polygons
          // @ts-ignore
            ? item.polygons.forEach(polygon => {
              uniqueFacies.add(polygon.facies.name)
            })
          // @ts-ignore
            : uniqueFacies.add(item.facies)
        })
      }
      minFacies = uniqueFacies.size
    } else {
      minFacies = 2
    }
  } else if ([type, rule.type].includes('bayfill')) {
    minFacies = 5
  } else {
    throw new Error(`${type} is not implemented`)
  }
  return minFacies
}

// @ts-ignore
function hasEnoughFacies (rule, getters: RootGetters): boolean {
  const numFacies = getters['facies/selected'].length
  return numFacies >= minFacies(rule, getters)
}

// @ts-ignore
const resolve = (path, obj = self, separator = '.'): object => {
  const properties = Array.isArray(path) ? path : path.split(separator)
  // @ts-ignore
  return properties.reduce((prev, curr) => prev && prev[`${curr}`], obj)
}

function sortAlphabetically<T extends Named> (arr: T[]): T[] {
  return Object.values(arr).sort((a, b): number => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)
}

function sortByProperty<T> (prop: string): (items: T[]) => T[] {
  return function (items: T[]): T[] {
    if (items instanceof Object) items = Object.values(items)
    items.forEach((item: T) => {
      if (!item.hasOwnProperty(prop)) {
        throw new Error(`The item (${item}) does not have the required property on which to sort (${prop})`)
      }
    })
    return items.slice().sort((polygon, other): number => polygon[`${prop}`] - other[`${prop}`])
  }
}

function sortByOrder<T> (items: T[], index: number, isDescending: boolean): T[] {
  // Used in Vuetify's tables
  return sortByProperty<T>('order')(items)
}

function toIdentifiedObject<T> (items: T[]): Identified<T> {
  items = Object.values(items)
  return items.reduce((obj, item): Identified<T> => {
    obj[getId(item)] = item
    return obj
  }, {})
}

export {
  getId,
  sortByProperty,
  sortByOrder,
  defaultSimulationSettings,
  makeData,
  makeTruncationRuleSpecification,
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
  toIdentifiedObject,
}

import flatten from 'flat'

import { Identifiable, Named, Parent } from '@/utils/domain/bases/interfaces'
import { OverlayPolygon, Polygon, TruncationRule } from '@/utils/domain'
import { APSError } from '@/utils/domain/errors'
import { BayfillSpecification } from '@/utils/domain/truncationRule/bayfill'
import { CubicSpecification } from '@/utils/domain/truncationRule/cubic'
import { NonCubicSpecification } from '@/utils/domain/truncationRule/nonCubic'
import { ID, Identified } from '@/utils/domain/types'
import {
  getId,
  newSeed,
  getRandomInt,
  isEmpty,
  notEmpty,
  allSet,
  isUUID,
  includes,
} from '@/utils/helpers'
import { hasParents } from '@/utils/domain/bases/zoneRegionDependent'
import { RootGetters } from '@/store/typing'

import uuidv5 from 'uuid/v5'
import { Vue } from 'vue/types/vue'

interface Newable<T> { new (...args: any[]): T }

function makeData<T extends Identifiable, Y extends Identifiable> (
  items: T[],
  _class: Newable<Y>,
  originals: T[] | null = null
): Identified<Y> {
  if (items.length === 0) return {}
  originals = originals ? Object.values(originals) : []
  const data = {}
  for (const item of items) {
    const instance = originals
      .find((original): boolean => Object.keys(item)
        .every((key): boolean => original[`${key}`] === item[`${key}`])
      ) || new _class(item)
    data[instance.id] = instance
  }
  return data
}

interface Coordinate2D {
  x: number
  y: number
}

interface Coordinate3D extends Coordinate2D {
  z: number
}

export interface SimulationSettings {
  gridAzimuth: number
  gridSize: Coordinate3D
  simulationBox: Coordinate3D
  simulationBoxOrigin: Coordinate2D
}

function defaultSimulationSettings (): SimulationSettings {
  return {
    gridAzimuth: 0,
    gridSize: { x: 100, y: 100, z: 1 },
    simulationBox: { x: 1000, y: 1000, z: 10 },
    simulationBoxOrigin: { x: 0, y: 0 },
  }
}

function simplify (specification: BayfillSpecification | NonCubicSpecification | CubicSpecification, rule: TruncationRule, includeOverlay: boolean = true) {
  if (specification instanceof Array) {
    return specification
      .map((spec, index) => {
        spec.facies = rule.polygons[`${index}`].id
        return spec
      })
  } else {
    // @ts-ignore
    specification.polygons = specification.polygons
      .filter((polygon: Polygon): boolean => polygon instanceof OverlayPolygon ? includeOverlay : true)
      .map((polygon: Polygon): Polygon => {
        // @ts-ignore
        polygon.facies = polygon.id
        polygon.fraction = 1
        return polygon
      })
    if (!includeOverlay) {
      specification.overlay = null
    }
    return specification
  }
}

function makeSimplifiedTruncationRuleSpecification (rule: TruncationRule) {
  return {
    type: rule.type,
    globalFaciesTable: (rule.backgroundPolygons as Polygon[])
      .map((polygon, index) => {
        return {
          code: index,
          name: polygon.id,
          probability: 1 / rule.backgroundPolygons.length,
          inZone: true,
          inRule: true,
        }
      }),
    gaussianRandomFields: ['GRF1', 'GRF2', 'GRF3']
      .map(field => {
        const included = !(field === 'GRF3' && rule.type !== 'bayfill')
        return {
          name: field,
          inZone: true,
          inRule: included,
          inBackground: included,
        }
      }),
    values: simplify(rule.specification, rule, false),
    constantParameters: true,
  }
}

function makeGlobalFaciesTableSpecification ({ rootGetters }: { rootGetters: RootGetters}, rule: TruncationRule) {
  const facies = rootGetters['facies/selected']
    .filter((facies): boolean => rootGetters.options.filterZeroProbability ? !!facies.previewProbability && facies.previewProbability > 0 : true)
  const cumulativeProbability = facies.reduce((cum, { previewProbability }): number => cum + Number(previewProbability), 0)

  return facies
    .map(({ facies: globalFacies, previewProbability, id }) => {
      let polygon = (rule.polygons as Polygon[]).find((polygon): boolean => getId(polygon.facies) === id)
      // @ts-ignore
      if (isEmpty(polygon) && rule.overlay) {
        // @ts-ignore
        polygon = Object.values(rule.overlay).find((polygon): boolean => polygon.facies.id === id)
      }
      return {
        code: globalFacies.code,
        name: globalFacies.name,
        probability: Number(previewProbability) / cumulativeProbability,
        inZone: true,
        inRule: Object.is(polygon, undefined) ? -1 : (polygon as Polygon).order,
      }
    })
}

function makeTruncationRuleSpecification (rule: TruncationRule, rootGetters: RootGetters) {
  return {
    type: rule.type,
    globalFaciesTable: makeGlobalFaciesTableSpecification({ rootGetters }, rule),
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

function goTroughChildren (component: Vue, onFound: (child: Vue) => any, breakEarly: boolean = false): void {
  let children = component.$children.slice()
  while (children.length > 0) {
    const child = children.shift()
    // @ts-ignore
    if (typeof child !== 'undefined' && child.dialog !== false) {
      if (child.$v && child.$v.$invalid) {
        onFound(child)
        if (breakEarly) break
      }
      children = children.concat(child.$children.slice())
    }
  }
}

function invalidateChildren (component: Vue): void {
  goTroughChildren(component, (child): void => child.$v.$touch())
}

function hasValidChildren (component: Vue): boolean {
  let valid = true
  goTroughChildren(component, (): void => { valid = false }, true)
  return valid
}

function hasCurrentParents (item: any, getters: RootGetters): boolean {
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
  const type = isUUID(rule.type)
    ? getters['truncationRules/typeById'](rule.type)
    : rule.type
  if (!type) throw new APSError(`There exists no types with the ID ${rule.type}`)
  if (
    [type, rule.type].includes('non-cubic')
    || [type, rule.type].includes('cubic')
  ) {
    if (rule.polygons) {
      // @ts-ignore
      const uniqueFacies = new Set(rule.polygons.map((polygon): string => faciesName(polygon)))
      if (rule.overlay) {
        const items = Object.values(rule.overlay.items || rule.overlay)
        items.forEach((item): void => {
          // @ts-ignore
          item.polygons
          // @ts-ignore
            ? item.polygons.forEach((polygon): void => {
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

function hasEnoughFacies (rule: TruncationRule, getters: RootGetters): boolean {
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

function getParameters (collection: object, delimiter: string = '.'): string[] {
  const parameters = new Set(Object.keys(collection))
  const selectable = Object.keys(flatten(collection, { delimiter }))
    .filter((param): boolean => param.endsWith('selected'))
    .map((param): string => param.slice(0, -'/selected'.length))
  selectable.forEach((param): void => {
    parameters.delete(param.split(delimiter)[0])
  })
  return [
    ...parameters,
    ...selectable,
  ]
}

export {
  getId,
  sortByProperty,
  sortByOrder,
  defaultSimulationSettings,
  makeData,
  makeSimplifiedTruncationRuleSpecification,
  makeTruncationRuleSpecification,
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
  getParameters,
  includes,
}

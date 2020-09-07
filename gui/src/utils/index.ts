import { Vue } from 'vue/types/vue'
import flatten from 'flat'
import { v5 as uuidv5 } from 'uuid'

import {
  Identifiable,
  Named,
  Ordered,
  SimulationSettings,
  Newable,
  Identified,
} from '@/utils/domain/bases/interfaces'
import { RootGetters, RootState } from '@/store/typing'

import { PolygonSpecification } from '@/utils/domain/polygon/base'
import { TruncationRule } from '@/utils/domain/truncationRule'
import { TruncationRuleSpecification, TruncationRuleType } from '@/utils/domain/truncationRule/base'
import { Parent, Polygon } from '@/utils/domain'
import { ID } from '@/utils/domain/types'

import { hasParents } from '@/utils/domain/bases/zoneRegionDependent'

import { APSError } from '@/utils/domain/errors'

import {
  allSet,
  getId,
  getRandomInt,
  hasOwnProperty,
  includes,
  isEmpty,
  isUUID,
  newSeed,
  notEmpty,
  identify,
} from '@/utils/helpers'

function makeData<C extends Identifiable, T> (
  items: T[],
  _class: Newable<C>,
  originals: Identified<C> | C[] | null = null
): Identified<C> {
  if (items.length === 0) return {}
  originals = originals ? Object.values(originals) : []
  const data = {}
  for (const item of items) {
    const instance = (originals
      .find((original): boolean => Object.keys(item)
        .every((key): boolean => original[`${key}`] === item[`${key}`])
      ) || new _class(item)) as C
    data[instance.id] = instance
  }
  return data
}

function defaultSimulationSettings (): SimulationSettings {
  return {
    gridAzimuth: 0,
    gridSize: { x: 100, y: 100, z: 1 },
    simulationBox: { x: 1000, y: 1000, z: 10 },
    simulationBoxOrigin: { x: 0, y: 0 },
  }
}

function simplify<P extends PolygonSpecification, Spec extends TruncationRuleSpecification<P>> (specification: Spec, includeOverlay = true): Spec {
  return {
    ...specification,
    polygons: specification.polygons
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      .filter((polygon: P): boolean => polygon.overlay ? includeOverlay : true)
      .map((polygon: P): P => {
        return {
          ...polygon,
          facies: polygon.id,
          fraction: 1,
        }
      }),
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    overlay: includeOverlay ? specification.overlay : null
  }
}

interface GlobalFaciesSpecification {
  code: number
  name: string
  probability: number
  inZone: boolean
  inRule: number | boolean
}

interface GaussianRandomFieldSpecification {
  name: string
  inZone: boolean
  inRule: number | boolean
  inBackground: boolean
}

export interface TruncationRuleDescription {
  type: TruncationRuleType
  globalFaciesTable: GlobalFaciesSpecification[]
  gaussianRandomFields: GaussianRandomFieldSpecification[]
  values: TruncationRuleSpecification
  constantParameters: boolean
}

function makeSimplifiedTruncationRuleSpecification (rule: TruncationRule): TruncationRuleDescription {
  return {
    type: rule.type,
    globalFaciesTable: (rule.backgroundPolygons as Polygon[])
      .map((polygon, index): GlobalFaciesSpecification => {
        return {
          code: index,
          name: polygon.id,
          probability: 1 / rule.backgroundPolygons.length,
          inZone: true,
          inRule: true,
        }
      }),
    gaussianRandomFields: ['GRF1', 'GRF2', 'GRF3']
      .map((field): GaussianRandomFieldSpecification => {
        const included = !(field === 'GRF3' && rule.type !== 'bayfill')
        return {
          name: field,
          inZone: true,
          inRule: included,
          inBackground: included,
        }
      }),
    values: simplify(rule.specification, false),
    constantParameters: true,
  }
}

function makeGlobalFaciesTableSpecification ({ rootGetters }: { rootGetters: RootGetters}, rule: TruncationRule): GlobalFaciesSpecification[] {
  const facies = rootGetters['facies/selected']
    .filter((facies): boolean => rootGetters.options.filterZeroProbability ? !!facies.previewProbability && facies.previewProbability > 0 : true)
  const cumulativeProbability = facies.reduce((cum, { previewProbability }): number => cum + Number(previewProbability), 0)

  return facies
    .map(({ facies: globalFacies, previewProbability, id }): GlobalFaciesSpecification => {
      let polygon = (rule.polygons as Polygon[]).find((polygon): boolean => getId(polygon.facies) === id)
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      if (isEmpty(polygon) && rule.overlay) {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
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

function makeGaussianRandomFieldSpecification (rule: TruncationRule): GaussianRandomFieldSpecification[] {
  return rule.fields
    .map((field): GaussianRandomFieldSpecification => {
      return {
        name: field.name,
        inZone: true,
        inRule: rule.fields.findIndex((item): boolean => item.id === field.id),
        inBackground: rule.isUsedInBackground(field),
      }
    })
}

function makeTruncationRuleSpecification (rule: TruncationRule, rootGetters: RootGetters): TruncationRuleDescription {
  return {
    type: rule.type,
    globalFaciesTable: makeGlobalFaciesTableSpecification({ rootGetters }, rule),
    gaussianRandomFields: makeGaussianRandomFieldSpecification(rule),
    values: rule.specification,
    constantParameters: !rootGetters.faciesTable.some((facies): boolean => !!facies.probabilityCube),
  }
}

function goTroughChildren (component: Vue, onFound: (child: Vue) => any, breakEarly = false): void {
  let children = component.$children.slice()
  while (children.length > 0) {
    const child = children.shift()
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
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

function faciesName (obj: any): any {
  if (hasOwnProperty(obj, 'facies')) obj = obj.facies
  if (hasOwnProperty(obj, 'name')) obj = obj.name
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
      const uniqueFacies = new Set(rule.polygons.map((polygon: any): string => faciesName(polygon)))
      if (rule.overlay) {
        const items = Object.values(rule.overlay.items || rule.overlay)
        items.forEach((item: any): void => {
          item.polygons
            ? item.polygons.forEach((polygon: any): void => {
              uniqueFacies.add(polygon.facies.name)
            })
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

const resolve = (path: string | string[], obj: any = self, separator = '.'): Record<string, unknown> => {
  const properties = Array.isArray(path) ? path : path.split(separator)
  return properties.reduce((prev, curr) => prev && prev[`${curr}`], obj)
}

function sortAlphabetically<T extends Named> (arr: T[]): T[] {
  return Object.values(arr)
    .sort((a, b): number => a.name.localeCompare(b.name))
}

function sortByProperty<T> (prop: string): (items: T[]) => T[] {
  return function (items: T[]): T[] {
    if (items instanceof Object) items = Object.values(items)
    items.forEach((item: T): void => {
      if (!hasOwnProperty(item, prop)) {
        throw new Error(`The item (${item}) does not have the required property on which to sort (${prop})`)
      }
    })
    return items.slice().sort((polygon, other): number => (polygon[`${prop}`] as number) - (other[`${prop}`] as number))
  }
}

function sortByOrder<T extends Ordered> (items: T[], index: number, isDescending: boolean): T[] {
  // Used in Vuetify's tables
  return sortByProperty<T>('order')(items)
}

function getParameters (collection: Record<string, unknown>, delimiter = '.'): string[] {
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

const encodeState = (state: RootState): string => btoa(JSON.stringify(state))

export {
  getId,
  sortByProperty,
  sortByOrder,
  defaultSimulationSettings,
  makeData,
  makeSimplifiedTruncationRuleSpecification,
  makeTruncationRuleSpecification,
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
  getParameters,
  includes,
  identify,
  encodeState,
}

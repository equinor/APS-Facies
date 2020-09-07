import { Context as RootContext, RootGetters, RootState } from '@/store/typing'
import { Parent } from '@/utils/domain'
import { Identified, ParentReference } from '@/utils/domain/bases/interfaces'
import ZoneRegionDependent from '@/utils/domain/bases/zoneRegionDependent'
import Polygon, { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'
import { Dispatch } from 'vuex'

type Context<S = Record<string, unknown>> = RootContext<S, RootGetters>

export function usesAllFacies<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> (
  { rootGetters }: { rootGetters: RootGetters },
  rule: TruncationRule<T, S, P>,
): boolean {
  const available = new Set(rootGetters['facies/selected'].map(({ id }): ID => id))
  const used = rule.polygons.reduce((facies, polygon): Set<ID> => {
    if (polygon.facies) {
      facies.add(polygon.facies.id)
    }
    return facies
  }, (new Set() as Set<ID>))
  return (
    available.size === used.size
    && [...available].every((id): boolean => used.has(id))
  )
}

export function isReady<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> (
  { rootGetters }: Context,
  rule: TruncationRule<T, S, P>,
): boolean {
  return (
    !!rule
    && rule.ready
    && usesAllFacies({ rootGetters }, rule)
  )
}

export interface Element {
  name: string
  items: ZoneRegionDependent[]
  serialization: string
}

function listify (obj: Identified<ZoneRegionDependent>): ZoneRegionDependent[] {
  return Object.values(obj)
}

export async function removeOld ({ dispatch }: { dispatch: Dispatch }, elements: Element[], target: Parent | ParentReference): Promise<void> {
  for (const element of elements) {
    for (const item of element.items.filter((item): boolean => item.isChildOf(target))) {
      await dispatch(`${element.name}/remove`, item, { root: true })
    }
  }
}

export function getElements ({ rootState }: { rootState: RootState }, exclude: string[] = []): Element[] {
  return [
    {
      name: 'gaussianRandomFields/crossSections',
      items: listify(rootState.gaussianRandomFields.crossSections.available),
      serialization: ''
    },
    { name: 'gaussianRandomFields', items: listify(rootState.gaussianRandomFields.available), serialization: '' },
    { name: 'facies', items: listify(rootState.facies.available), serialization: '' },
    { name: 'facies/groups', items: listify(rootState.facies.groups.available), serialization: '' },
    { name: 'truncationRules', items: listify(rootState.truncationRules.available), serialization: '' },
  ]
    .filter(({ name }): boolean => !exclude.includes(name))
}

export async function removeFaciesDependent (context: { rootState: RootState, dispatch: Dispatch }): Promise<void> {
  const { rootState } = context
  const parents: Parent[] = []

  for (const zone of Object.values(rootState.zones.available)) {
    if (zone.hasRegions) {
      for (const region of zone.regions) {
        parents.push({ zone, region })
      }
    } else {
      parents.push({ zone, region: null })
    }
  }

  const elements = getElements(context, ['gaussianRandomFields/crossSections', 'gaussianRandomFields']).reverse()
  await Promise.all(parents.map(parent => removeOld(context, elements, parent)))
}

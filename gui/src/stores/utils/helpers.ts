import type { Dependent, Parent } from '@/utils/domain'
import type { ParentReference } from '@/utils/domain/bases/interfaces'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type Polygon from '@/utils/domain/polygon/base'
import type { TruncationRuleSerialization } from '@/utils/domain/truncationRule/base'
import type TruncationRule from '@/utils/domain/truncationRule/base'
import type { ID } from '@/utils/domain/types'
import { useFaciesStore } from '@/stores/facies'
import { useGaussianRandomFieldCrossSectionStore } from '@/stores/gaussian-random-fields/cross-sections'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import { deserializeTruncationRule, useTruncationRuleStore } from '@/stores/truncation-rules'
import type { DependentConfiguration } from '@/utils/domain/bases/zoneRegionDependent'
import { hasParents } from '@/utils/domain/bases/zoneRegionDependent'
import type { FaciesSerialization } from '@/utils/domain/facies/local'
import type Facies from '@/utils/domain/facies/local'
import type { FaciesGroupSerialization } from '@/utils/domain/facies/group'
import { resolveParentReference } from '@/stores/utils'

export function usesAllFacies<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
  RULE extends TruncationRule<T, S, P>,
>(
  rule: RULE,
): boolean {
  const faciesStore = useFaciesStore()
  const available = new Set(
    faciesStore.selected.map(({ id }): ID => id),
  )
  const used = rule.polygons.reduce((facies, polygon): Set<ID> => {
    if (polygon.facies) {
      facies.add(polygon.facies.id)
    }
    return facies
  }, new Set() as Set<ID>)
  return (
    available.size === used.size &&
    [...available].every((id): boolean => used.has(id))
  )
}

export function isReady<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
>(rule: TruncationRule<T, S, P>): boolean {
  return !!rule && rule.ready && usesAllFacies(rule)
}

export interface Element {
  name: string
  items: Array<Dependent & { id: ID }>
  serialization: string
  add: (item: DependentConfiguration) => void
  remove: (item: Dependent) => void
}

export function removeOld(
  elements: Element[],
  target: Parent | ParentReference,
): void {
  for (const element of elements) {
    for (const item of element.items.filter((item): boolean =>
      item.isChildOf(target),
    )) {
      element.remove(item)
    }
  }
}

export function getRelevant<T extends Dependent>(available: T[], parent: Parent): T[] {
  return available.filter(item => hasParents(item, parent.zone, parent.region))
}

export function getElements(
  exclude: string[] = [],
): Element[] {
  function extractFromStore(store: () => any) {
    const { remove, add, available } = store()
    return {
      remove,
      add,
      items: available,
    }
  }
  return [
    {
      name: 'gaussianRandomFields/crossSections',
      serialization: '',
      ...extractFromStore(useGaussianRandomFieldCrossSectionStore),
    },
    {
      name: 'gaussianRandomFields',
      serialization: '',
      ...extractFromStore(useGaussianRandomFieldStore),
    },
    {
      name: 'facies',
      serialization: '',
      ...(() => {
        const { remove, add, available } = useFaciesStore()
        return {
          remove,
          add: (serialization: FaciesSerialization) => {
            add(
              serialization.facies,
              resolveParentReference(serialization.parent),
              serialization.probabilityCube,
              serialization.previewProbability,
              serialization.id,
              )
          },
          items: available,
        }
      })(),
    },
    {
      name: 'facies/groups',
      serialization: '',
      ...(() => {
        const { remove, add, available } = useFaciesGroupStore()
        const { byId } = useFaciesStore()
        return {
          remove,
          add: (serialization: FaciesGroupSerialization) => {
            add(
              serialization.facies.map(id => byId(id) as Facies),
              resolveParentReference(serialization.parent),
              serialization.id,
            )
          },
          items: available,
        }
      })(),
    },
    {
      name: 'truncationRules',
      serialization: '',
      ...(() => {
        const { remove, add, available } = useTruncationRuleStore()
        return {
          remove,
          add: (serialization: TruncationRuleSerialization) => {
            add(deserializeTruncationRule(serialization))
          },
          items: available,
        }
      })()
    },
  ].filter(({ name }): boolean => !exclude.includes(name))
}

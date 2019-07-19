import { RootGetters, RootState } from '@/store/typing'
import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'

interface Context {
  rootState: RootState
  rootGetters: RootGetters
}

export function usesAllFacies<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
> (
  { rootGetters }: { rootGetters: RootGetters },
  rule: TruncationRule<T, S>,
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
> (
  { rootGetters }: Context,
  rule: TruncationRule<T, S>,
): boolean {
  return (
    !!rule
    && rule.ready
    && usesAllFacies({ rootGetters }, rule)
  )
}

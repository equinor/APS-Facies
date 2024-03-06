import type GlobalFacies from '@/utils/domain/facies/global'
import type Facies from '@/utils/domain/facies/local'
import type Polygon from '@/utils/domain/polygon/base'
import { getFaciesName } from '@/utils/domain/polygon/base'
import type { Identified } from '@/utils/domain/bases/interfaces'
import { getId, hasOwnProperty } from '@/utils/helpers'

interface Counts {
  [id: string]: number
}

export function hasFaciesSpecifiedForMultiplePolygons(
  polygons: Polygon[] | Identified<Polygon>,
  facies: Facies | GlobalFacies | null = null,
  ignoreEmptyFacies = true,
): boolean {
  if (polygons instanceof Object) polygons = Object.values(polygons)
  if (!polygons || polygons.length === 0) return false
  const faciesCount: Counts = polygons
    .filter((polygon): boolean =>
      facies ? getId(polygon.facies) === getId(facies) : true,
    )
    .reduce((counts: Counts, { facies }): Counts => {
      const id = getId(facies)
      if (ignoreEmptyFacies && !id) return counts
      hasOwnProperty(counts, id) ? (counts[id] += 1) : (counts[id] = 1)
      return counts
    }, {})
  return Object.values(faciesCount).some((count): boolean => count > 1)
}

export { getFaciesName }

export const relativeTo = (base: string, path: string): string => {
  // Assumed to be UNIX paths
  if (!path.startsWith('/')) {
    // The path we compare to, is already relative
    return path
  }
  const parents = {
    base: base.split('/'),
    path: path.split('/'),
  }
  const commonParentIndex = parents.base.reduce(
    (commonIndex, directory, index) =>
      index < parents.path.length && directory === parents.path[index]
        ? index
        : commonIndex,
    0,
  )
  const remaining = {
    base: parents.base.slice(commonParentIndex + 1),
    path: parents.path.slice(commonParentIndex + 1),
  }
  return [...remaining.base.map(() => '..'), ...remaining.path].join('/')
}

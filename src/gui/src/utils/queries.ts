import GlobalFacies from '@/utils/domain/facies/global'
import Facies from '@/utils/domain/facies/local'
import Polygon, { getFaciesName } from '@/utils/domain/polygon/base'
import { Identified } from '@/utils/domain/bases/interfaces'
import { getId, hasOwnProperty } from '@/utils/helpers'

interface Counts {
  [id: string]: number
}

export function hasFaciesSpecifiedForMultiplePolygons (
  polygons: Polygon[] | Identified<Polygon>,
  facies: Facies | GlobalFacies | null = null,
  ignoreEmptyFacies = true,
): boolean {
  if (polygons instanceof Object) polygons = Object.values(polygons)
  if (!polygons || polygons.length === 0) return false
  const faciesCount: Counts = polygons
    .filter((polygon): boolean => facies ? getId(polygon.facies) === getId(facies) : true)
    .reduce((counts: Counts, { facies }): Counts => {
      const id = getId(facies)
      if (ignoreEmptyFacies && !id) return counts
      hasOwnProperty(counts, id)
        ? counts[`${id}`] += 1
        : counts[`${id}`] = 1
      return counts
    }, {})
  return Object.values(faciesCount).some((count): boolean => count > 1)
}

export {
  getFaciesName,
}
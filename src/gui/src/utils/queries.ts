import GlobalFacies from '@/utils/domain/facies/global'
import Facies from '@/utils/domain/facies/local'
import Polygon from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'
import { Identified } from '@/utils/domain/types'
import { getId } from '@/utils/helpers'
import { RootGetters } from '@/utils/helpers/store/typing'

function hasFaciesSpecifiedForMultiplePolygons (polygons: Polygon[] | Identified<Polygon>, facies: Facies | GlobalFacies | null = null): boolean {
  if (polygons instanceof Object) polygons = Object.values(polygons)
  if (!polygons || polygons.length === 0) return false
  const faciesCount = polygons
    .filter(polygon => facies ? getId(polygon.facies) === getId(facies) : true)
    .reduce((counts, { facies }) => {
      const id = getId(facies)
      counts.hasOwnProperty(id)
        ? counts[`${id}`] += 1
        : counts[`${id}`] = 1
      return counts
    }, {})
  return Object.values(faciesCount).some((count): boolean => count > 1)
}

function availableForBackgroundFacies (getters: RootGetters, rule: TruncationRule<Polygon>, facies: Facies) {
  return !getters['facies/groups/used'](facies)
    && rule.backgroundPolygons.map(({ facies }) => getId(facies)).includes(getId(facies))
}

export {
  hasFaciesSpecifiedForMultiplePolygons,
  availableForBackgroundFacies,
}

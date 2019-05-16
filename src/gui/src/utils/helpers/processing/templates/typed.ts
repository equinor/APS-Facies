import APSTypeError from '@/utils/domain/errors/type'
import BayfillPolygon from '@/utils/domain/polygon/bayfill'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import OverlayPolygon from '@/utils/domain/polygon/overlay'

type Polygon = BayfillPolygon | NonCubicPolygon | OverlayPolygon

export function makePolygonsFromSpecification (polygons: any[]): Polygon[] {
  return polygons.map((polygon): Polygon => {
    if (
      'order' in polygon
      && 'facies' in polygon
    ) {
      if ('angle' in polygon) {
        return new NonCubicPolygon(polygon)
      } else if (
        (
          'group' in polygon
          && 'field' in polygon
        ) || (
          'overlay' in polygon
          && polygon.overlay
        )
      ) {
        return new OverlayPolygon(polygon)
      } else if (
        'name' in polygon
        || 'slantFactor' in polygon /* No all Bayfill polygons has slantFactor */
      ) {
        return new BayfillPolygon(polygon)
      } else {
        throw new APSTypeError('The given polygon is not recognised')
      }
    } else {
      throw new APSTypeError('The given polygon is not recognised')
    }
  })
}

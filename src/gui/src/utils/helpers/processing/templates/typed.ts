import APSTypeError from '@/utils/domain/errors/type'
import BayfillPolygon from '@/utils/domain/polygon/bayfill'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import OverlayPolygon from '@/utils/domain/polygon/overlay'

type Polygon = BayfillPolygon | NonCubicPolygon | OverlayPolygon

export function makePolygonsFromSpecification (polygons: any[]): Polygon[] {
  return polygons.map(polygon => {
    if ('overlay' in polygon) {
      if (!polygon.overlay) {
        if ('angle' in polygon) return new NonCubicPolygon(polygon)
        /* TODO: Look for Cubic */
        else return new BayfillPolygon(polygon)
      } else return new OverlayPolygon(polygon)
    } else throw new APSTypeError('The given polygon is not recognised')
  })
}

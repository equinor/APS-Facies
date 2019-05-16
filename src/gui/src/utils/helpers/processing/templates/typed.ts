import { getId } from '@/utils'
import APSTypeError from '@/utils/domain/errors/type'
import BayfillPolygon from '@/utils/domain/polygon/bayfill'
import CubicPolygon from '@/utils/domain/polygon/cubic'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import Cubic from '@/utils/domain/truncationRule/cubic'

type Polygon = BayfillPolygon | NonCubicPolygon | CubicPolygon | OverlayPolygon

export function makePolygonsFromSpecification (polygons: any[]): Polygon[] {
  const parsedPolygons = polygons.map((polygon): Polygon => {
    if (
      'order' in polygon
      && 'facies' in polygon
    ) {
      if ('angle' in polygon) {
        return new NonCubicPolygon(polygon)
      } else if (
        (
          'children' in polygon
          && 'parent' in polygon
        ) || (
          // From a template
          'level' in polygon
        )
      ) {
        return new CubicPolygon(polygon)
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
  return parsedPolygons
    .map((polygon): Polygon => {
      if (polygon instanceof CubicPolygon) {
        if (polygon.parent === null) {
          // This is the root
          return polygon
        } else {
          const parent = parsedPolygons.find((item): boolean => item.id === getId(polygon.parent))
          if (!(parent instanceof CubicPolygon)) {
            throw new APSTypeError(`The parent reference of ${polygon.id}, is not a Cubic Polygon`)
          }
          polygon.parent = (parent as CubicPolygon)
        }
      }
      return polygon
    })
}

export function normalizeOrder (rule: Cubic, cb: (polygon: OverlayPolygon | CubicPolygon, order: number) => void): void {
  [...Array(rule.levels + 1)].forEach((_, level): void => {
    // @ts-ignore TS2445
    const polygons = (Object.values(rule._polygons) as (OverlayPolygon | CubicPolygon)[])
      .filter((polygon): boolean => polygon.atLevel === level)
      .sort((a, b): number => a.order - b.order)
    polygons
      .forEach((polygon, index): void => {
        const order = index + 1
        if (polygon.order !== order) {
          cb(polygon, order)
        }
      })
  })
}

import { getId } from '@/utils'
import APSTypeError from '@/utils/domain/errors/type'
import BayfillPolygon from '@/utils/domain/polygon/bayfill'
import CubicPolygon from '@/utils/domain/polygon/cubic'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import Cubic from '@/utils/domain/truncationRule/cubic'

type Polygon = BayfillPolygon | NonCubicPolygon | CubicPolygon | OverlayPolygon

function addChildren (polygon: CubicPolygon, parsedPolygons: Polygon[]): void {
  polygon.children = polygon.children.map((child): CubicPolygon => {
    const found = parsedPolygons.find((polygon): boolean => polygon.id === getId(child))
    if (!found || !(found instanceof CubicPolygon)) {
      throw new APSTypeError(`The child reference of ${found ? found.id : found}, is not a Cubic Polygon`)
    }
    return found
  })
}

function addParent (polygon: CubicPolygon, parsedPolygons: Polygon[]): void {
  const parent = parsedPolygons.find((item): boolean => item.id === getId(polygon.parent))
  if (!(parent instanceof CubicPolygon)) {
    throw new APSTypeError(`The parent reference of ${polygon.id}, is not a Cubic Polygon`)
  }
  polygon.parent = (parent as CubicPolygon)
}

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
        if (polygon.parent !== null) {
          // This is the root
          addParent(polygon, parsedPolygons)
        }
        addChildren(polygon, parsedPolygons)
      }
      return polygon
    })
}

export function normalizeOrder (rule: Cubic, cb: (polygon: OverlayPolygon | CubicPolygon, order: number) => void): void {
  const polygons = rule.root ? [...rule.root.children] : []
  while (polygons.length > 0) {
    const polygon = polygons.shift()
    if (!polygon) continue
    const children = polygon.children
      .concat() /* Copy the array, because `sort` sorts in-place */
      .sort((a, b): number => a.order - b.order)
    children.forEach((child, index): void => {
      polygons.push(child)
      const order = index + 1
      if (child.order !== order) {
        cb(child, order)
      }
    })
  }
}
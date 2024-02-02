import type { TruncationRuleTemplateType } from '@/stores/truncation-rules/templates/types'
import { APSError } from '@/utils/domain/errors'
import type { TruncationRule, Cubic } from '@/utils/domain/truncationRule'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import { useFaciesStore } from '@/stores/facies'
import type {
  Facies,
  FaciesGroup,
  GaussianRandomField,
  Parent,
  ParentReference,
  Polygon,
} from '@/utils/domain'
import type {
  PolygonArgs,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type { ID } from '@/utils/domain/types'
import type { TruncationRuleTemplateFromJson } from './templates'
import { isArray } from 'lodash'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import type {
  OverlayPolygonArgs,
  OverlayPolygonSerialization
} from '@/utils/domain/polygon/overlay'
import OverlayPolygon, {
  isOverlayPolygonSerialization
} from '@/utils/domain/polygon/overlay'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import NonCubicPolygon, {
  type NonCubicPolygonArgs,
} from '@/utils/domain/polygon/nonCubic'
import CubicPolygon, {
  type CubicPolygonArgs,
} from '@/utils/domain/polygon/cubic'
import BayfillPolygon, {
  type BayfillPolygonArgs,
  hasBayfillName
} from '@/utils/domain/polygon/bayfill'
import APSTypeError from '@/utils/domain/errors/type'
import { getId } from '@/utils'
import { useZoneStore } from '@/stores/zones'


function getOverlayItems(rule: Parameters<typeof minFacies>[0]): ({
  polygons: {
    facies: {
      name: string
    }
  }[]
} | {
  facies: string
})[] | null {
  if (rule instanceof OverlayTruncationRule)
    return rule.specification.overlay
  if ('overlay' in rule && rule.overlay) {
    if ('items' in rule.overlay) {
      console.error(rule.overlay)
      throw new Error('NotImplemented')
      // return rule.overlay.items
    }
    return rule.overlay
  }
  return null
}

export function minFacies<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends TruncationRule<T, S, P>,
>(
  rule:
    | RULE
    | TruncationRuleTemplateType
    | TruncationRuleTemplateFromJson,
): number {
  let minFacies = 0
  const type = rule.type
  if (!type) throw new APSError(`There exists no types with the ID ${type}`)
  if (
    [type, rule.type].includes('non-cubic') ||
    [type, rule.type].includes('cubic')
  ) {
    if (rule.polygons) {
      const uniqueFacies = new Set(
        (rule.polygons as Array<Polygon>).filter((p) => p.facies).map((p) => p.facies!.name),
      )
      const items = getOverlayItems(rule)
      if (items !== null && items !== undefined) {
        items.forEach((item: any): void => {
          item.polygons
            ? item.polygons.forEach((polygon: any): void => {
                uniqueFacies.add(polygon.facies.name)
              })
            : uniqueFacies.add(item.facies)
        })
      }
      minFacies = uniqueFacies.size
    } else {
      minFacies = 2
    }
  } else if ([type, rule.type].includes('bayfill')) {
    minFacies = 5
  } else {
    throw new Error(`${type} is not implemented`)
  }
  return minFacies
}

export function hasEnoughFacies<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends TruncationRule<T, S, P>,
>(
  rule:
    | RULE
    | TruncationRuleTemplateType
    | TruncationRuleTemplateFromJson,
): boolean {
  const faciesStore = useFaciesStore()
  const numFacies = faciesStore.selected.length
  return numFacies >= minFacies(rule)
}

export function usesAllFacies<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends TruncationRule<T, S, P>,
>(rule: RULE): boolean {
  const faciesStore = useFaciesStore()
  const available = new Set(faciesStore.selected.map(({ id }) => id))
  const used = rule.polygons.reduce((facies, polygon) => {
    if (polygon.facies) facies.add(polygon.facies.id)
    return facies
  }, new Set() as Set<ID>)
  return (
    available.size === used.size &&
    [...available].every((id): boolean => used.has(id))
  )
}

type RealizedPolygon = BayfillPolygon | NonCubicPolygon | CubicPolygon | OverlayPolygon

function addChildren(polygon: CubicPolygon, parsedPolygons: RealizedPolygon[]): void {
  polygon.children = polygon.children.map((child): CubicPolygon => {
    const found = parsedPolygons.find(
      (polygon): boolean => polygon.id === getId(child),
    )
    if (!found || !(found instanceof CubicPolygon)) {
      throw new APSTypeError(
        `The child reference of ${
          found ? found.id : found
        }, is not a Cubic Polygon`,
      )
    }
    return found
  })
}

function addParent(polygon: CubicPolygon, parsedPolygons: RealizedPolygon[]): void {
  const parent = parsedPolygons.find(
    (item): boolean => item.id === getId(polygon.parent),
  )
  if (!(parent instanceof CubicPolygon)) {
    throw new APSTypeError(
      `The parent reference of ${polygon.id}, is not a Cubic Polygon`,
    )
  }
  polygon.parent = parent as CubicPolygon
}

export type PartiallySpecifiedPolygonSpecification = (PolygonArgs | NonCubicPolygonArgs | CubicPolygonArgs | BayfillPolygonArgs) & {
  facies: Facies | null
  field?: GaussianRandomField | null
  group?: FaciesGroup
}

export function makePolygonsFromSpecification<
    S extends PartiallySpecifiedPolygonSpecification
>(polygons: S[]): RealizedPolygon[] {
  const parsedPolygons = polygons.map((polygon): RealizedPolygon => {
    if ('order' in polygon && 'facies' in polygon) {
      if ('angle' in polygon) {
        return new NonCubicPolygon(polygon)
      } else if (
          ('children' in polygon && 'parent' in polygon) ||
          // From a template
          'level' in polygon
      ) {
        // We implement the hierarchy in `organizeCubicPolygons`
        // we therefore set `parent` and `children` to be empty
        return new CubicPolygon({
          order: polygon.order,
          parent: 'parent' in  polygon ? polygon.parent : null,
          facies: polygon.facies,
          children: 'children' in polygon? polygon.children : [],
          id: polygon.id,
          fraction: polygon.fraction,
        })
      } else if (
          ('group' in polygon && 'field' in polygon) ||
          ('overlay' in polygon && polygon.overlay)
      ) {
        return new OverlayPolygon(polygon as OverlayPolygonArgs)
      } else if (
          ('name' in polygon) && hasBayfillName(polygon.name as string)
          // 'slantFactor' in polygon /* No all Bayfill polygons has slantFactor */
      ) {
        return new BayfillPolygon(polygon as BayfillPolygonArgs)
      } else {
        throw new APSTypeError('The given polygon is not recognised')
      }
    } else {
      throw new APSTypeError('The given polygon is not recognised')
    }
  })
  return parsedPolygons.map((polygon) => {
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

export function deserializePolygons<S extends PolygonSerialization | OverlayPolygonSerialization>(polygons: S[]) {
  const faciesStore = useFaciesStore()
  const gaussianRandomFieldStore = useGaussianRandomFieldStore()
  const faciesGroupStore = useFaciesGroupStore()
  const partiallyDefinedPolygons: PartiallySpecifiedPolygonSpecification[] = polygons.map((polygon) => {
      const facies = polygon.facies ? faciesStore.byId(polygon.facies) : null
      if (isArray(facies)) throw new Error('')
      if (isOverlayPolygonSerialization(polygon)) {
        return ({
          ...polygon,
          facies,
          field: polygon.field ? gaussianRandomFieldStore.byId(polygon.field) : null,
          group: faciesGroupStore.byId(polygon.group),
        })
      } else return ({
        ...polygon,
        facies,
      } as PartiallySpecifiedPolygonSpecification)
    })
  return makePolygonsFromSpecification(partiallyDefinedPolygons)
}


export function resolveParentReference(
  parent: ParentReference | Parent,
): Parent {
  const zoneStore = useZoneStore()
  const zone = zoneStore.identifiedAvailable[getId(parent.zone)]
  if (!zone)
    throw new Error(`The zone with reference '${parent.zone}' is missing`)
  const region =
    zone.regions.find((region) => region.id === getId(parent.region)) || null
  return {
    zone,
    region,
  }
}

export function normalizeOrder(
  rule: Cubic,
  cb: (polygon: OverlayPolygon | CubicPolygon, order: number) => void,
): void {
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

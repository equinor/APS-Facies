import APSError from '@/utils/domain/errors/base'
import type GaussianRandomField from '@/utils/domain/gaussianRandomField'
import type FaciesGroup from '@/utils/domain/facies/group'
import type { ID } from '@/utils/domain/types'
import type {
  PolygonArgs,
  PolygonSerialization,
  PolygonSpecification,
} from './base'
import Polygon from './base'
import type { MaybeFmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'

export type CENTER = MaybeFmuUpdatable

export interface OverlayPolygonArgs extends PolygonArgs {
  group: FaciesGroup
  center?: number
  field?: GaussianRandomField | null
}

export interface OverlayPolygonSpecification extends PolygonSpecification {
  center: CENTER
  field: string
  over: string[]
}

export interface OverlayPolygonSerialization extends PolygonSerialization {
  group: ID
  center: CENTER
  field: ID | null
}

export default class OverlayPolygon extends Polygon {
  public center: CENTER
  public field: GaussianRandomField | null
  public readonly group: FaciesGroup

  public constructor({
    group,
    center = 0,
    field = null,
    ...rest
  }: OverlayPolygonArgs) {
    super(rest)
    if (!group) throw new APSError('No group was given')
    this.group = group
    this.center = center
    this.field = field
  }

  public get overlay(): boolean {
    return true
  }

  public get specification(): OverlayPolygonSpecification {
    return {
      ...super.specification,
      center: this.center,
      field: this.field ? this.field.name : '',
      over: this.group.facies.map((facies): string => facies.name),
    }
  }

  public toJSON(): OverlayPolygonSerialization {
    return {
      ...super.toJSON(),
      group: this.group.id,
      center: this.center,
      field: this.field ? this.field.id : null,
    } as OverlayPolygonSerialization
  }
}

export function isOverlayPolygonSerialization(polygon: PolygonSerialization): polygon is OverlayPolygonSerialization {
  return polygon.overlay
}

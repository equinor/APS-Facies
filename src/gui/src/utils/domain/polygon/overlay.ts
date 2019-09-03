import APSError from '@/utils/domain/errors/base'
import GaussianRandomField from '@/utils/domain/gaussianRandomField'
import FaciesGroup from '@/utils/domain/facies/group'
import { ID } from '@/utils/domain/types'
import Polygon, { PolygonArgs, PolygonSerialization, PolygonSpecification } from './base'

export type CENTER = number

export interface OverlayPolygonArgs extends PolygonArgs {
  group: FaciesGroup
  center?: number
  field?: GaussianRandomField | null
}

export interface OverlayPolygonSpecification extends PolygonSpecification {
  center: number
  field: string
  over: string[]
}

export interface OverlayPolygonSerialization extends PolygonSerialization {
  group: ID
  center: number
  field: ID | null
}

export default class OverlayPolygon extends Polygon {
  public center: CENTER
  public field: GaussianRandomField | null
  public readonly group: FaciesGroup

  public constructor ({ group, center = 0, field = null, ...rest }: OverlayPolygonArgs) {
    super(rest)
    if (!group) throw new APSError('No group was given')
    this.group = group
    this.center = center
    this.field = field
  }

  public get overlay (): boolean { return true }

  public get specification (): OverlayPolygonSpecification {
    return {
      ...super.specification,
      center: this.center,
      field: this.field ? this.field.name : '',
      over: this.group.facies.map((facies): string => facies.name),
    }
  }

  public toJSON (): OverlayPolygonSerialization {
    return {
      ...super.toJSON(),
      group: this.group.id,
      center: this.center,
      field: this.field ? this.field.id : null,
    }
  }
}

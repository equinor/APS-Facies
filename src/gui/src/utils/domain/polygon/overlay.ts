import APSError from '@/utils/domain/errors/base'
import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import FaciesGroup from '@/utils/domain/facies/group'
import Polygon, { PolygonArgs } from './base'

export type CENTER = number

export default class OverlayPolygon extends Polygon {
  public center: CENTER
  public field: GaussianRandomField | null
  public readonly group: FaciesGroup

  public constructor ({ group, center = 0, field = null, ...rest }: PolygonArgs & {
    group: FaciesGroup
    center: number
    field: GaussianRandomField | null
  }) {
    super(rest)
    if (!group) throw new APSError('No group was given')
    this.group = group
    this.center = center
    this.field = field
  }

  public get overlay (): boolean { return true }
}

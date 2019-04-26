import FmuUpdatableValue, { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import Polygon, { PolygonArgs } from '@/utils/domain/polygon/base'

export type NonCubicPolygonArgs = PolygonArgs & {
  angle?: FmuUpdatable | number
}

export default class NonCubicPolygon extends Polygon {
  public angle: FmuUpdatable

  public constructor ({ angle = 0, ...rest }: NonCubicPolygonArgs) {
    super(rest)
    this.angle = new FmuUpdatableValue(angle)
  }
}

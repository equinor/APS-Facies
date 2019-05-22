import FmuUpdatableValue, { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import Polygon, { PolygonArgs, PolygonSpecification } from '@/utils/domain/polygon/base'

export type NonCubicPolygonArgs = PolygonArgs & {
  angle?: FmuUpdatable | number
}

export interface NonCubicPolygonSpecification extends PolygonSpecification {
  angle: FmuUpdatable
  updatable: boolean
}

export default class NonCubicPolygon extends Polygon {
  public angle: FmuUpdatable

  public constructor ({ angle = 0, ...rest }: NonCubicPolygonArgs) {
    super(rest)
    this.angle = new FmuUpdatableValue(angle)
  }

  public get specification (): NonCubicPolygonSpecification {
    return {
      ...this.specification,
      angle: this.angle,
      updatable: this.angle.updatable,
    }
}

import type {
  FmuUpdatable,
} from '@/utils/domain/bases/fmuUpdatable'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import type {
  PolygonArgs,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import Polygon from '@/utils/domain/polygon/base'

export type NonCubicPolygonArgs = PolygonArgs & {
  angle?: FmuUpdatable | number
}

export interface NonCubicPolygonSpecification extends PolygonSpecification {
  angle: FmuUpdatable
  updatable: boolean
}

export interface NonCubicPolygonSerialization extends PolygonSerialization {
  angle: FmuUpdatable
}

export default class NonCubicPolygon extends Polygon {
  public angle: FmuUpdatable

  public constructor({ angle = 0, ...rest }: NonCubicPolygonArgs) {
    super(rest)
    this.angle = new FmuUpdatableValue(angle)
  }

  public get isFmuUpdatable(): boolean {
    return super.isFmuUpdatable || this.angle.updatable
  }

  public get specification(): NonCubicPolygonSpecification {
    return {
      ...super.specification,
      angle: this.angle,
      updatable: this.angle.updatable,
    }
  }

  public toJSON(): NonCubicPolygonSerialization {
    return {
      ...super.toJSON(),
      angle: this.angle,
    }
  }
}

import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

interface Angle {
  azimuth: FmuUpdatableValue
  stacking: FmuUpdatableValue
  migration: FmuUpdatableValue
}

interface Origin {
  x: FmuUpdatableValue
  y: FmuUpdatableValue
  z: FmuUpdatableValue
  type: string
}

export default class Trend {
  public use: boolean
  public type: string
  public angle: Angle
  public stackingDirection: string
  public parameter: string | null
  public curvature: FmuUpdatableValue
  public origin: Origin
  public relativeSize: FmuUpdatableValue
  public relativeStdDev: FmuUpdatableValue

  public constructor ({
    use = false,
    type = 'LINEAR',
    azimuth = 0,
    azimuthUpdatable = false,
    stackAngle = 2.0,
    stackAngleUpdatable = false,
    migrationAngle = 0,
    migrationAngleUpdatable = false,
    stackingDirection = 'PROGRADING',
    parameter = null,
    curvature = 1,
    curvatureUpdatable = false,
    originX = 0.5,
    originXUpdatable = false,
    originY = 0.5,
    originYUpdatable = false,
    originZ = 0.5,
    originZUpdatable = false,
    originType = 'RELATIVE',
    relativeSize = 0,
    relativeSizeUpdatable = false,
    relativeStdDev = 0.001,
    relativeStdDevUpdatable = false,
  }) {
    this.use = use
    this.type = type
    this.angle = {
      azimuth: new FmuUpdatableValue(azimuth, !!azimuthUpdatable),
      stacking: new FmuUpdatableValue(stackAngle, !!stackAngleUpdatable),
      migration: new FmuUpdatableValue(migrationAngle, !!migrationAngleUpdatable),
    }
    this.stackingDirection = stackingDirection
    this.parameter = parameter
    if (this.type === 'HYPERBOLIC' && curvature <= 1) curvature = 1.01
    this.curvature = new FmuUpdatableValue(curvature, !!curvatureUpdatable)
    this.origin = {
      x: new FmuUpdatableValue(originX, !!originXUpdatable),
      y: new FmuUpdatableValue(originY, !!originYUpdatable),
      z: new FmuUpdatableValue(originZ, !!originZUpdatable),
      type: originType,
    }
    this.relativeSize = new FmuUpdatableValue(relativeSize, !!relativeSizeUpdatable)
    this.relativeStdDev = new FmuUpdatableValue(relativeStdDev, !!relativeStdDevUpdatable)
  }
}

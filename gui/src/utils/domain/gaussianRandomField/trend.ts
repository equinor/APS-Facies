import type { FmuUpdatableSerialization } from '@/utils/domain/bases/fmuUpdatable'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

export type TrendType =
  | 'NONE'
  | 'LINEAR'
  | 'ELLIPTIC'
  | 'ELLIPTIC_CONE'
  | 'HYPERBOLIC'
  | 'RMS_PARAM'
  | 'RMS_TRENDMAP'
export type StackingDirectionType = 'PROGRADING' | 'RETROGRADING'
export type OriginType = 'RELATIVE' | 'ABSOLUTE'

interface Angle {
  azimuth: FmuUpdatableValue
  stacking: FmuUpdatableValue
  migration: FmuUpdatableValue
}

interface AngleSerialization {
  azimuth: FmuUpdatableSerialization
  stacking: FmuUpdatableSerialization
  migration: FmuUpdatableSerialization
}

interface Origin {
  x: FmuUpdatableValue
  y: FmuUpdatableValue
  z: FmuUpdatableValue
  type: OriginType
}

interface OriginSerialization {
  x: FmuUpdatableSerialization
  y: FmuUpdatableSerialization
  z: FmuUpdatableSerialization
  type: OriginType
}

export interface TrendConfiguration {
  use?: boolean
  type?: TrendType
  azimuth?: number
  azimuthUpdatable?: boolean
  stackAngle?: number
  stackAngleUpdatable?: boolean
  migrationAngle?: number
  migrationAngleUpdatable?: boolean
  stackingDirection?: StackingDirectionType
  parameter?: string | null
  trendMapName?: string | null
  trendMapZone?: string | null
  curvature?: number
  curvatureUpdatable?: boolean
  originX?: number
  originXUpdatable?: boolean
  originY?: number
  originYUpdatable?: boolean
  originZ?: number
  originZUpdatable?: boolean
  originType?: OriginType
  relativeSize?: number
  relativeSizeUpdatable?: boolean
  relativeStdDev?: number
  relativeStdDevUpdatable?: boolean
}

export interface TrendSerialization {
  use: boolean
  type: TrendType
  angle: AngleSerialization
  stackingDirection: StackingDirectionType
  origin: OriginSerialization
  parameter: string | null
  trendMapName: string | null
  trendMapZone: string | null
  curvature: FmuUpdatableSerialization
  relativeSize: FmuUpdatableSerialization
  relativeStdDev: FmuUpdatableSerialization
}

export function unpackTrend(trend: TrendSerialization): TrendConfiguration {
  return {
    use: trend.use,
    type: trend.type,
    azimuth: trend.angle.azimuth.value,
    azimuthUpdatable: trend.angle.azimuth.updatable,
    stackAngle: trend.angle.stacking.value,
    stackAngleUpdatable: trend.angle.stacking.updatable,
    migrationAngle: trend.angle.migration.value,
    migrationAngleUpdatable: trend.angle.migration.updatable,
    stackingDirection: trend.stackingDirection,
    parameter: trend.parameter,
    trendMapName: trend.trendMapName,
    trendMapZone: trend.trendMapZone,
    curvature: trend.curvature.value,
    curvatureUpdatable: trend.curvature.updatable,
    originX: trend.origin.x.value,
    originXUpdatable: trend.origin.x.updatable,
    originY: trend.origin.y.value,
    originYUpdatable: trend.origin.y.updatable,
    originZ: trend.origin.z.value,
    originZUpdatable: trend.origin.z.updatable,
    originType: trend.origin.type,
    relativeSize: trend.relativeSize.value,
    relativeSizeUpdatable: trend.relativeSize.updatable,
    relativeStdDev: trend.relativeStdDev.value,
    relativeStdDevUpdatable: trend.relativeStdDev.updatable,
  }
}

export default class Trend {
  public use: boolean
  public type: TrendType
  public angle: Angle
  public stackingDirection: StackingDirectionType
  public parameter: string | null
  public trendMapName: string | null
  public trendMapZone: string | null
  public curvature: FmuUpdatableValue
  public origin: Origin
  public relativeSize: FmuUpdatableValue
  public relativeStdDev: FmuUpdatableValue

  public constructor({
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
    trendMapName = null,
    trendMapZone = null,
    curvature = 1,
    curvatureUpdatable = false,
    originX = 0.5,
    originXUpdatable = false,
    originY = 0.5,
    originYUpdatable = false,
    originZ = 0.5,
    originZUpdatable = false,
    originType = 'RELATIVE',
    relativeSize = 1,
    relativeSizeUpdatable = false,
    relativeStdDev = 0.001,
    relativeStdDevUpdatable = false,
  }: TrendConfiguration) {
    this.use = use
    this.type = type
    this.angle = {
      azimuth: new FmuUpdatableValue(azimuth, !!azimuthUpdatable),
      stacking: new FmuUpdatableValue(stackAngle, !!stackAngleUpdatable),
      migration: new FmuUpdatableValue(
        migrationAngle,
        !!migrationAngleUpdatable,
      ),
    }
    this.stackingDirection = stackingDirection
    this.parameter = parameter
    this.trendMapName = trendMapName
    this.trendMapZone = trendMapZone
    if (this.type === 'HYPERBOLIC' && curvature <= 1) curvature = 1.01
    this.curvature = new FmuUpdatableValue(curvature, !!curvatureUpdatable)
    if (this.type === 'ELLIPTIC_CONE') originZ = 0
    this.origin = {
      x: new FmuUpdatableValue(originX, !!originXUpdatable),
      y: new FmuUpdatableValue(originY, !!originYUpdatable),
      z: new FmuUpdatableValue(originZ, !!originZUpdatable),
      type: originType,
    }
    this.relativeSize = new FmuUpdatableValue(
      relativeSize,
      !!relativeSizeUpdatable,
    )
    this.relativeStdDev = new FmuUpdatableValue(
      relativeStdDev,
      !!relativeStdDevUpdatable,
    )
  }

  public get isFmuUpdatable(): boolean {
    return (
      this.relativeStdDev.updatable ||
      (this.type !== 'RMS_PARAM' &&
        this.type !== 'RMS_TRENDMAP' &&
        (this.angle.azimuth.updatable ||
          this.angle.stacking.updatable ||
          (this.type !== 'LINEAR' &&
            (this.curvature.updatable ||
              this.origin.x.updatable ||
              this.origin.y.updatable ||
              (['ELLIPTIC', 'HYPERBOLIC'].includes(this.type) &&
                this.origin.z.updatable) ||
              (['ELLIPTIC_CONE', 'HYPERBOLIC'].includes(this.type) &&
                (this.angle.migration.updatable ||
                  this.relativeSize.updatable))))))
    )
  }

  public toJSON(): TrendSerialization {
    return {
      use: this.use,
      type: this.type,
      angle: { ...this.angle },
      stackingDirection: this.stackingDirection,
      origin: { ...this.origin },
      parameter: this.parameter,
      trendMapName: this.trendMapName,
      trendMapZone: this.trendMapZone,
      curvature: this.curvature.toJSON(),
      relativeSize: this.relativeSize.toJSON(),
      relativeStdDev: this.relativeStdDev.toJSON(),
    }
  }
}

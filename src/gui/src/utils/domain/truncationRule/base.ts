import { Named } from '@/utils/domain/bases'
import ZoneRegionDependent, { DependentConfiguration } from '@/utils/domain/bases/zoneRegionDependent'
import APSTypeError from '@/utils/domain/errors/type'
import Facies from '@/utils/domain/facies/local'
import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import Polygon from '@/utils/domain/polygon/base'
import { FRACTION, ID, Identified } from '@/utils/domain/types'
import { getId, identify, allSet } from '@/utils/helpers'

export type TruncationRuleConfiguration<T extends Polygon> = DependentConfiguration & {
  name: string
  polygons: Identified<T> | T[]
  backgroundFields: GaussianRandomField[]
  realization?: number[][]
}

export interface Specification {
  facies: string
  fraction: FRACTION
  order: number
}

export default abstract class TruncationRule<T extends Polygon> extends ZoneRegionDependent implements Named {
  public readonly name: string

  public realization: number[][] | null

  protected _polygons: Identified<T>
  protected _backgroundFields: GaussianRandomField[]
  protected _constraints: (() => boolean)[]

  protected constructor ({ name, polygons, backgroundFields, realization, ...rest }: TruncationRuleConfiguration<T>) {
    super(rest)
    this.name = name
    this._polygons = identify(polygons)
    this._backgroundFields = backgroundFields
    this.realization = realization || null

    this._constraints = [
      (): boolean => allSet(this.polygons, 'facies'),
      (): boolean => this.polygons.length > 0,
    ]
  }

  abstract get type (): string

  public get ready (): boolean {
    return this._constraints.every((constraint): boolean => constraint())
  }
  public abstract get specification (): Specification[] | object

  public get backgroundFields (): GaussianRandomField[] {
    return Object.values(this._backgroundFields)
  }

  public get fields (): GaussianRandomField[] {
    return this.backgroundFields
  }

  public get useOverlay (): boolean { return false }

  public get backgroundPolygons (): T[] {
    return this.polygons
  }

  public get polygons (): T[] {
    return Object.values(this._polygons)
      .sort((a, b): number => a.atLevel === b.atLevel ? a.order - b.order : b.atLevel - a.atLevel)
  }

  public isUsedInDifferentAlpha (field: GaussianRandomField | ID, channel: number): boolean {
    // Channel is 1-indexed, while order of fields are 0-indexed
    return this.backgroundFields.findIndex((item): boolean => item.id === getId(field)) !== (channel - 1)
  }

  public isUsedInBackground (item: GaussianRandomField | Facies): boolean {
    if (item instanceof GaussianRandomField) {
      return this.backgroundFields.some((field): boolean => field.id === item.id)
    } else if (item instanceof Facies) {
      for (const { facies } of this.backgroundPolygons) {
        if (facies && facies.id === item.id) {
          return true
        }
      }
      return false
    } else {
      throw new APSTypeError(`${item} is not valid`)
    }
  }
}

export type TruncationRules<T extends Polygon> = Identified<TruncationRule<T>>
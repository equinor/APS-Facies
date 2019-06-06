import { Named } from '@/utils/domain/bases'
import ZoneRegionDependent, {
  DependentConfiguration,
  DependentSerialization,
} from '@/utils/domain/bases/zoneRegionDependent'
import APSTypeError from '@/utils/domain/errors/type'
import Facies from '@/utils/domain/facies/local'
import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import Polygon, { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import { ID, Identified } from '@/utils/domain/types'
import { getId, identify, allSet } from '@/utils/helpers'

export interface TruncationRuleSerialization<S extends PolygonSerialization> extends DependentSerialization {
  name: string
  type: string
  polygons: S[]
  backgroundFields: ID[]
  realization: number[][] | null
}

export type TruncationRuleConfiguration<T extends Polygon> = DependentConfiguration & {
  name: string
  polygons: Identified<T> | T[]
  backgroundFields: GaussianRandomField[]
  realization?: number[][]
}

export default abstract class TruncationRule<
  T extends Polygon,
  S extends PolygonSerialization,
> extends ZoneRegionDependent implements Named {
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
      (): boolean => this.normalizedFractions,
    ]
  }

  abstract get type (): string

  public get ready (): boolean {
    return this._constraints.every((constraint): boolean => constraint())
  }
  public abstract get specification (): PolygonSpecification[] | object

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
    const index = this.backgroundFields.findIndex((item): boolean => item.id === getId(field))
    return index < 0
      ? false
      // Channel is 1-indexed, while order of fields are 0-indexed
      : index !== (channel - 1)
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

  public get normalizedFractions (): boolean {
    return this.polygons.every((polygon): boolean => this.isPolygonFractionsNormalized(polygon))
  }

  public isPolygonFractionsNormalized (polygon: T): boolean {
    const sum = this.polygons
      .filter(({ facies }): boolean => getId(facies) === getId(polygon.facies))
      .reduce((sum, polygon): number => polygon.fraction + sum, 0)
    return sum === 1
  }

  protected toJSON (): TruncationRuleSerialization<S> {
    return {
      ...super.toJSON(),
      type: this.type,
      name: this.name,
      parent: this.parent,
      polygons: Object.values(this._polygons).map((polygon): S => (polygon.toJSON() as S)),
      backgroundFields: this.backgroundFields.map((field): ID => field.id),
      realization: this.realization,
    }
  }
}

export type TruncationRules<T extends Polygon, S extends PolygonSerialization> = Identified<TruncationRule<T, S>>

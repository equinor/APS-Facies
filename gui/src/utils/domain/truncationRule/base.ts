import type { Named } from '@/utils/domain/bases'
import type { Identified } from '@/utils/domain/bases/interfaces'
import type {
  SimulationConfiguration,
  SimulationSerialization,
} from '@/utils/domain/bases/simulation'
import Simulation from '@/utils/domain/bases/simulation'
import APSTypeError from '@/utils/domain/errors/type'
import Facies from '@/utils/domain/facies/local'
import type {
  GaussianRandomFieldSerialization,
} from '@/utils/domain/gaussianRandomField'
import GaussianRandomField from '@/utils/domain/gaussianRandomField'
import type {
  Polygon,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type { ID } from '@/utils/domain/types'
import { getId, identify, allSet } from '@/utils/helpers'
import { isCloseToUnity } from '@/utils/helpers/simple'

export interface TruncationRuleSerialization<
  S extends PolygonSerialization = PolygonSerialization,
> extends SimulationSerialization {
  name: string
  type: TruncationRuleType
  polygons: S[]
  backgroundFields: ID[]
}

export type TruncationRuleType = 'bayfill' | 'non-cubic' | 'cubic'

export const truncationRuleTypeNames: Record<TruncationRuleType, string> = {
  bayfill: 'Bayfill',
  'non-cubic': 'Non-Cubic',
  cubic: 'Cubic',
}

export type TruncationRuleConfiguration<T extends Polygon> =
  SimulationConfiguration & {
    name: string
    polygons: Identified<T> | T[]
    backgroundFields: (GaussianRandomField | null)[]
  }

export interface TruncationRuleSpecification<
  P extends PolygonSpecification,
> {
  polygons: P[]
}

export default abstract class TruncationRule<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
  >
  extends Simulation
  implements Named
{
  public readonly name: string

  protected _requiredGaussianFields: number
  protected _polygons: Identified<T>
  protected _backgroundFields: (GaussianRandomField | null)[]
  protected _constraints: [() => boolean, string][]

  protected constructor({
    name,
    polygons,
    backgroundFields,
    ...rest
  }: TruncationRuleConfiguration<T>) {
    super(rest)
    this.name = name
    this._polygons = identify(polygons)
    this._backgroundFields = backgroundFields
    this._requiredGaussianFields = 2

    this._constraints = [
      [
        (): boolean => allSet(this.polygons, 'facies'),
        'Some polygons does not have a facies assigned to it',
      ],
      [
        (): boolean => this.polygons.length > 0,
        'No polygons have been specified',
      ],
      [
        (): boolean => this.normalizedFractions,
        'Some fraction of facies does not sum to one',
      ],
      [
        (): boolean => isCloseToUnity(this.cumulativeFaciesProbability),
        'The sum of facies probabilities does not sum to one',
      ],
      [
        (): boolean =>
          this.backgroundFields.filter((field): boolean => !!field).length ===
          this._requiredGaussianFields,
        `The truncation rule must have ${this._requiredGaussianFields} background fields`,
      ],
      [
        (): boolean => this.fields.every((field): boolean => field.valid),
        'Some field is invalid',
      ],
    ]
  }

  abstract get type(): TruncationRuleType

  public get ready(): boolean {
    return this._constraints.every(([constraint]): boolean => constraint())
  }

  public get isFmuUpdatable(): boolean {
    return (
      this.fields.some((field) => field.isFmuUpdatable) ||
      this.polygons.some((polygon) => polygon.isFmuUpdatable)
    )
  }

  public get realization(): number[][] | null {
    return this.simulation
  }
  public set realization(data) {
    this.simulation = data
  }

  public get errorMessage(): string | undefined {
    for (const [constraint, error] of this._constraints) {
      if (!constraint()) return error
    }
    return undefined
  }

  public abstract get specification(): TruncationRuleSpecification<P>

  public get backgroundFields(): (GaussianRandomField | null)[] {
    return this._backgroundFields
  }

  public get fields(): GaussianRandomField[] {
    const fields: GaussianRandomField[] = []
    this.backgroundFields.forEach((field): void => {
      if (field) fields.push(field)
    })
    return fields
  }

  public get useOverlay(): boolean {
    return false
  }

  public get backgroundPolygons(): T[] {
    return this.polygons
  }

  public get polygons(): T[] {
    return Object.values(this._polygons).sort((a, b): number =>
      a.atLevel === b.atLevel ? a.order - b.order : b.atLevel - a.atLevel,
    )
  }

  public addPolygon(polygon: T) {
    this._polygons[polygon.id] = polygon
  }

  public removePolygon(polygon: T) {
    delete this._polygons[polygon.id]
  }

  public isUsedInDifferentAlpha(
    field: GaussianRandomField | ID,
    channel: number,
  ): boolean {
    const index = this.backgroundFields.findIndex(
      (item): boolean => getId(item) === getId(field),
    )
    return index < 0
      ? false
        : index !== channel - 1 /* Channel is 1-indexed, while order of fields are 0-indexed */
  }

  public isUsedInBackground(item: GaussianRandomField | Facies): boolean {
    if (item instanceof GaussianRandomField) {
      return this.backgroundFields.some(
        (field): boolean => getId(field) === item.id,
      )
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

  public get normalizedFractions(): boolean {
    return this.polygons.every((polygon): boolean =>
      this.isPolygonFractionsNormalized(polygon),
    )
  }

  public isPolygonFractionsNormalized<T extends Polygon>(polygon: T): boolean {
    const sum = this.polygons
      .filter(({ facies }): boolean => getId(facies) === getId(polygon.facies))
      .reduce((sum, polygon): number => polygon.fraction + sum, 0)
    return isCloseToUnity(sum)
  }

  protected toJSON(): TruncationRuleSerialization<S> {
    return {
      ...super.toJSON(),
      type: this.type,
      name: this.name,
      polygons: Object.values(this._polygons).map(
        (polygon): S => polygon.toJSON() as S,
      ),
      backgroundFields: this.backgroundFields.map((field): ID => getId(field)),
    }
  }

  protected _hashify(): any {
    const spec: TruncationRuleSerialization<S> & {
      fields?: GaussianRandomFieldSerialization[]
    } = this.toJSON()
    spec.fields = this.fields.map((field) => field.toJSON())
    return spec
  }

  private get facies(): Facies[] {
    const facies: Set<Facies> = new Set()
    for (const polygon of this.polygons) {
      if (polygon.facies) {
        facies.add(polygon.facies)
      }
    }
    return [...facies]
  }

  private get cumulativeFaciesProbability(): number {
    return this.facies.reduce(
      (sum, { previewProbability }): number => sum + (previewProbability || 0),
      0,
    )
  }
}

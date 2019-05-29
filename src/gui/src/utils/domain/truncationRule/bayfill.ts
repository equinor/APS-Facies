import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import BayfillPolygon, {
  BayfillPolygonSerialization,
  BayfillPolygonSpecification
} from '@/utils/domain/polygon/bayfill'
import TruncationRule, { TruncationRuleConfiguration } from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'

export type BayfillSpecification = BayfillPolygonSpecification[]

export default class Bayfill extends TruncationRule<BayfillPolygon, BayfillPolygonSerialization> {
  public constructor (props: TruncationRuleConfiguration<BayfillPolygon>) {
    super(props)

    this._constraints.push(...[
      (): boolean => this.fields.length === 3,
      (): boolean => this.polygons.length === 5,
      (): boolean => (new Set(this.polygons.map(({ facies }): ID | null => facies ? facies.id : facies))).size === 5,
      (): boolean => {
        return this.polygons.reduce((numHasFacies, polygon): number => {
          if (polygon.facies) numHasFacies += 1
          return numHasFacies
        }, 0) === 5
      }
    ])
  }

  public get fields (): GaussianRandomField[] {
    return Object.values(this._backgroundFields)
  }

  public get backgroundFields (): GaussianRandomField[] {
    return this.fields
  }

  public get specification (): BayfillSpecification {
    return this.polygons
      .filter((polygon): boolean => !!polygon.slantFactor)
      .map((polygon): BayfillPolygonSpecification => polygon.specification)
  }

  public get type (): string {
    return 'bayfill'
  }
}

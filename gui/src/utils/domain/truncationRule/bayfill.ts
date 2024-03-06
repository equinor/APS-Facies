import type BayfillPolygon from '@/utils/domain/polygon/bayfill'
import {
  type BayfillPolygonSerialization,
  type BayfillPolygonSpecification,
} from '@/utils/domain/polygon/bayfill'
import type {
  TruncationRuleConfiguration,
  TruncationRuleSpecification,
} from '@/utils/domain/truncationRule/base'
import TruncationRule from '@/utils/domain/truncationRule/base'
import type { ID } from '@/utils/domain/types'

export type BayfillSpecification =
  TruncationRuleSpecification<BayfillPolygonSpecification>

export default class Bayfill extends TruncationRule<
  BayfillPolygon,
  BayfillPolygonSerialization,
  BayfillPolygonSpecification
> {
  public constructor(props: TruncationRuleConfiguration<BayfillPolygon>) {
    super(props)

    this._requiredGaussianFields = 3

    const additionalConstraints: [() => boolean, string][] = [
      [
        (): boolean => this.fields.length === this._requiredGaussianFields,
        `3 Gaussian Random Fields must be used (${this.fields.length} was given)`,
      ],
      [
        (): boolean => this.polygons.length === 5,
        'A Bayfill truncation rule must have exactly 5 polygons',
      ],
      [
        (): boolean =>
          new Set(
            this.polygons.map(({ facies }): ID | null =>
              facies ? facies.id : facies,
            ),
          ).size === 5,
        'A Bayfill truncation rule must use exactly 5 facies',
      ],
      [
        (): boolean => {
          return (
            this.polygons.reduce((numHasFacies, polygon): number => {
              if (polygon.facies) numHasFacies += 1
              return numHasFacies
            }, 0) === 5
          )
        },
        'All facies of a Bayfill truncation rule must be unique',
      ],
    ]
    this._constraints.push(...additionalConstraints)
  }

  public get specification(): BayfillSpecification {
    return {
      polygons: this.polygons
        .filter((polygon): boolean => !!polygon.slantFactor)
        .map((polygon): BayfillPolygonSpecification => polygon.specification),
    }
  }

  public get type(): 'bayfill' {
    return 'bayfill'
  }

  public toJSON() {
    return super.toJSON()
  }
}

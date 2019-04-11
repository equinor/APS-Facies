import { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import BayfillPolygon from '@/utils/domain/polygon/bayfill'
import TruncationRule, { Specification, TruncationRuleConfiguration } from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'

interface BayfillPolygonSpecification extends Specification {
  name: string
  polygon: string
  factor: FmuUpdatable
}

export default class Bayfill extends TruncationRule<BayfillPolygon> {
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

  public get specification (): BayfillPolygonSpecification[] {
    const _mapping: {[_: string]: string} = {
      'Bayhead Delta': 'SBHD',
      'Floodplain': 'SF',
      'Subbay': 'YSF',
    }
    return this.polygons
      .filter((polygon): boolean => !!polygon.slantFactor)
      .map((polygon): BayfillPolygonSpecification => {
        return {
          facies: polygon.facies ? polygon.facies.name : '',
          factor: (polygon.slantFactor as FmuUpdatable),
          fraction: polygon.fraction,
          name: _mapping[polygon.name],
          order: polygon.order,
          polygon: polygon.name,
        }
      })
  }

  public get type (): string {
    return 'bayfill'
  }
}

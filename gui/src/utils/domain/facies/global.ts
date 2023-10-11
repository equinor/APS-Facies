import type { Parent } from '@/utils/domain/bases/zoneRegionDependent'
import Discrete, {
  type DiscreteConfiguration,
  type DiscreteSerialization,
} from '@/utils/domain/bases/discrete'
import type { Color } from '@/utils/domain/facies/helpers/colors'
import type { Optional } from '@/utils/typing'
import type { CODE } from '@/utils/domain/types'

interface Observations {
  zones: number[]
  regions: number[]
}

interface Configuration extends DiscreteConfiguration {
  observed?: Optional<Observations>
  color: Color
  alias?: string
}

export interface GlobalFaciesSerialization extends DiscreteSerialization {
  observed: Optional<Observations>
  color: Color
  alias: string
}

export default class GlobalFacies extends Discrete {
  public observed: Optional<Observations>
  public color: Color
  public alias: string
  // make fields writable
  public declare name: string
  public declare code: CODE

  public constructor({
    observed = null,
    alias,
    color,
    ...rest
  }: Configuration) {
    super(rest)
    this.observed = observed
    this.color = color
    this.alias = alias || rest.name
  }

  public isObserved({ zone, region }: Partial<Parent>): boolean {
    if (!this.observed) return false
    if (!zone) return false
    const regionNumber = region ? region.code : 0
    return (
      this.observed.zones.includes(zone.code) &&
      this.observed.regions.includes(regionNumber)
    )
  }

  public toJSON(): GlobalFaciesSerialization {
    return {
      ...super.toJSON(),
      observed: this.observed,
      color: this.color,
      alias: this.alias,
    }
  }
}

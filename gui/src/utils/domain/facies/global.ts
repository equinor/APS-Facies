import { Parent } from '@/utils/domain/bases/zoneRegionDependent'
import Discrete, {
  DiscreteConfiguration,
  DiscreteSerialization,
} from '@/utils/domain/bases/discrete'
import { Color } from '@/utils/domain/facies/helpers/colors'
import { Optional } from '@/utils/typing'

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

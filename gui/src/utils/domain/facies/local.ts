import type {
  DependentConfiguration,
  DependentSerialization,
} from '@/utils/domain/bases/zoneRegionDependent'
import ZoneRegionDependent from '@/utils/domain/bases/zoneRegionDependent'
import type GlobalFacies from '@/utils/domain/facies/global'
import type { ID, PROBABILITY } from '@/utils/domain/types'
import type { Branded } from '@/utils/typing/simple'

export type ProbabilityCube = Branded<string, 'ProbabilityCube'>

export type FaciesConfiguration = DependentConfiguration & {
  facies: GlobalFacies
  probabilityCube?: ProbabilityCube | null
  previewProbability?: PROBABILITY | null
}

export interface FaciesSerialization extends DependentSerialization {
  facies: ID
  probabilityCube: ProbabilityCube | null
  previewProbability: PROBABILITY | null
}

export default class Facies extends ZoneRegionDependent {
  public readonly facies: GlobalFacies
  public probabilityCube: ProbabilityCube | null
  public previewProbability: PROBABILITY | null

  public constructor({
    facies,
    probabilityCube = null,
    previewProbability = null,
    ...rest
  }: FaciesConfiguration) {
    super(rest)
    this.facies = facies
    this.probabilityCube = probabilityCube
    this.previewProbability = previewProbability
  }

  public get name(): string {
    return this.facies.name
  }

  public get alias(): string {
    return this.facies.alias
  }

  public get code(): number {
    return this.facies.code
  }

  public get observed(): boolean {
    return this.facies.isObserved(this.parent)
  }

  public toJSON(): FaciesSerialization {
    return {
      ...super.toJSON(),
      facies: this.facies.id,
      probabilityCube: this.probabilityCube,
      previewProbability: this.previewProbability,
    }
  }
}

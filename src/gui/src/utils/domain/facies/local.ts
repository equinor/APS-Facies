import ZoneRegionDependent, {
  DependentConfiguration,
  DependentSerialization
} from '@/utils/domain/bases/zoneRegionDependent'
import GlobalFacies from '@/utils/domain/facies/global'
import { ID } from '@/utils/domain/types'

type Probability = number

// TODO: Make ProbabilityCube into its own class
export type ProbabilityCube = string

export type FaciesConfiguration = DependentConfiguration & {
  facies: GlobalFacies
  probabilityCube?: ProbabilityCube | null
  previewProbability?: Probability | null
}

export interface FaciesSerialization extends DependentSerialization {
  facies: ID
  probabilityCube: ProbabilityCube | null
  previewProbability: Probability | null
}

export default class Facies extends ZoneRegionDependent {
  public readonly facies: GlobalFacies
  public probabilityCube: ProbabilityCube | null
  public previewProbability: Probability | null

  public constructor ({
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

  public get name (): string { return this.facies.name }
  public get alias (): string { return this.facies.alias }
  public get code (): number { return this.facies.code }

  public get observed (): boolean {
    return this.facies.isObserved(this.parent)
  }

  public toJSON (): FaciesSerialization {
    return {
      ...super.toJSON(),
      facies: this.facies.id,
      probabilityCube: this.probabilityCube,
      previewProbability: this.previewProbability,
    }
  }
}

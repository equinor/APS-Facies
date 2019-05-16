import ZoneRegionDependent, { DependentConfiguration } from '@/utils/domain/bases/zoneRegionDependent'
import GlobalFacies from '@/utils/domain/facies/global'

type Probability = number

// TODO: Make ProbabilityCube into its own class
type ProbabilityCube = string

export type FaciesArgs = DependentConfiguration & {
  facies: GlobalFacies
  probabilityCube?: ProbabilityCube | null
  previewProbability?: Probability | null
}

export default class Facies extends ZoneRegionDependent {
  public readonly facies: GlobalFacies
  public probabilityCube: ProbabilityCube | null
  public previewProbability: Probability | null

  public constructor ({
    facies,
    probabilityCube = null,
    previewProbability = null,
    ...rest }: FaciesArgs) {
    super(rest)
    this.facies = facies
    this.probabilityCube = probabilityCube
    this.previewProbability = previewProbability
  }

  public get name (): string { return this.facies.name }
  public get alias (): string { return this.facies.alias }
}

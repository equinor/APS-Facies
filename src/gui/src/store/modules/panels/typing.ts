import { Optional } from '@/utils/typing'

export interface PanelsState {
  selection: {
    zoneRegion: boolean
    facies: boolean
  }
  preview: {
    truncationRuleMap: boolean
    truncationRuleRealization: boolean
    gaussianRandomFields: boolean
    crossPlots: boolean
  }
  settings: {
    faciesProbability: boolean
    truncationRule: boolean
    gaussianRandomFields: Optional<number> | boolean
  }
}

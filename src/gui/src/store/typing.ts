import { ConstantsState } from '@/store/modules/constants/typing'
import { GaussianRandomFieldState } from '@/store/modules/gaussianRandomFields/typing'
import MessageState from '@/store/modules/message/typing'
import OptionsState from '@/store/modules/options/typing'
import { PanelsState } from '@/store/modules/panels/typing'
import ParametersState from '@/store/modules/parameters/typing'
import PresetState from '@/store/modules/truncationRules/preset/typing'
import { TruncationRuleTemplateState } from '@/store/modules/truncationRules/typing'
import { Identified, SimulationSettings } from '@/utils/domain/bases/interfaces'
import { PolygonSerialization } from '@/utils/domain/polygon/base'
import { Commit, Dispatch } from 'vuex'

import { GridModel, GridModelsState } from '@/store/modules/gridModels/types'
import CopyPasteState from '@/store/modules/copyPaste/typing'
import { Polygon, TruncationRule, Parent } from '@/utils/domain'
import TruncationRuleBase from '@/utils/domain/truncationRule/base'
import GlobalFacies from '@/utils/domain/facies/global'
import FaciesGroup from '@/utils/domain/facies/group'
import Facies from '@/utils/domain/facies/local'
import GaussianRandomField from '@/utils/domain/gaussianRandomField'
import CrossSection from '@/utils/domain/gaussianRandomField/crossSection'
import Region from '@/utils/domain/region'
import { ID } from '@/utils/domain/types'
import Zone from '@/utils/domain/zone'

interface Context<S, G> {
  state: S
  getters: G
  commit: Commit
  dispatch: Dispatch
  rootState: RootState
  rootGetters: RootGetters
}

interface Store {
  state: RootState
  getters: RootGetters
  dispatch: Dispatch
  commit: Commit
}

interface RootState {
  _loaded: boolean
  _loading: {
    value: boolean
    message: string
  }

  constants: ConstantsState

  copyPaste: CopyPasteState

  message: MessageState

  panels: PanelsState

  gridModels: GridModelsState

  gaussianRandomFields: GaussianRandomFieldState & {
    crossSections: {
      available: Identified<CrossSection>
    }
  }

  facies: {
    available: Identified<Facies>
    groups: {
      available: Identified<FaciesGroup>
    }
    global: {
      available: Identified<GlobalFacies>
      current: ID
    }
  }

  parameters: ParametersState

  truncationRules: {
    available: Identified<TruncationRule>
    preset: PresetState
    templates: {
      available: Identified<{
        id: ID
        name: string
        type: string
        minFields: number
        polygons: {
          name: number
          facies: {
            name: string
            index: number
          }
          proportion: number
        }[]
        settings: object
        fields: {
          channel: number
          field: {
            name: string
            index: number
          }
        }[]
      }>
      types: TruncationRuleTemplateState
    }
  }

  options: OptionsState

  zones: {
    available: Identified<Zone>
    current: ID
  }
  regions: {
    available: Identified<Region>
    current: ID
    use: boolean
  }
}

interface RootGetters {
  'allFields': GaussianRandomField[]

  'gridModel': GridModel
  'blockedWellParameter': string
  'blockedWellLogParameter': string

  'regionParameter': string

  'facies': GlobalFacies
  'faciesTable': Facies[]

  'facies/byId': (faciesId: ID) => Facies | null
  'facies/selected': Facies[]
  'facies/constantProbability': (parent?: Parent) => boolean
  'facies/availableForBackgroundFacies': (rule: TruncationRuleBase<Polygon, PolygonSerialization>, facies: Facies) => boolean

  'facies/global/selected': GlobalFacies[]

  'facies/groups/used': (facies: Facies) => boolean

  'fields': GaussianRandomField[]

  'truncationRule': TruncationRule
  'truncationRules/typeById': (id: ID) => string | null
  'truncationRules/ruleTypes': { text: string, disabled: boolean, order: number }[]

  'gaussianRandomFields/crossSections/current': CrossSection | null
  'gaussianRandomFields/crossSections/byId': (id: ID) => CrossSection | null
  'gaussianRandomFields/crossSections/byParent': ({ parent }: { parent: Parent }) => CrossSection | null

  options: {
    filterZeroProbability: boolean
  }
  'region': Region
  'zone': Zone

  simulationSettings: (field?: GaussianRandomField) => SimulationSettings
}

export {
  Store,
  RootState,
  RootGetters,
  Context,
}

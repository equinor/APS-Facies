import { ConstantsState } from '@/store/modules/constants/typing'
import { FmuState } from '@/store/modules/fmu/typing'
import { GaussianRandomFieldState } from '@/store/modules/gaussianRandomFields/typing'
import MessageState from '@/store/modules/message/typing'
import OptionsState from '@/store/modules/options/typing'
import { PanelsState } from '@/store/modules/panels/typing'
import ParametersState from '@/store/modules/parameters/typing'
import PresetState from '@/store/modules/truncationRules/preset/typing'
import { TruncationRuleTemplateState } from '@/store/modules/truncationRules/typing'
import { Identified, SimulationSettings } from '@/utils/domain/bases/interfaces'
import { Color } from '@/utils/domain/facies/helpers/colors'
import GridModel from '@/utils/domain/gridModel'
import { PolygonSerialization } from '@/utils/domain/polygon/base'
import { Optional } from '@/utils/typing'
import { Commit, Dispatch } from 'vuex'

import { GridModelsState } from '@/store/modules/gridModels/types'
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
  version: string
  _loaded: {
    value: boolean
    loading: boolean
  }
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

  fmu: FmuState

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
  mayLoadParameters: boolean

  'allFields': GaussianRandomField[]

  'gridModel': string
  'gridModels': string[]

  'gridModels/name': string[]
  'gridModels/current': Optional<GridModel>

  'blockedWellParameter': string
  'blockedWellLogParameter': string

  'constants/faciesColors/byCode': (code: number) => Color

  'regionParameter': string

  'fmuMode': boolean
  'fmuUpdatable': boolean

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

  simulationSettings: ({ field, zone }: { field?: GaussianRandomField, zone?: Zone }) => SimulationSettings
  'zones/byCode': (zoneNumber: number, regionNumber?: Optional<number>) => Parent
}

export {
  Store,
  RootState,
  RootGetters,
  Context,
}

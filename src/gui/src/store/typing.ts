import { Commit, Dispatch } from 'vuex'

import { GridModelsState } from '@/store/modules/gridModels/types'
import { Polygon, TruncationRule } from '@/utils/domain'
import TruncationRuleBase from '@/utils/domain/truncationRule/base'
import { Parent } from '@/utils/domain/bases/interfaces'
import GlobalFacies from '@/utils/domain/facies/global'
import FaciesGroup from '@/utils/domain/facies/group'
import Facies from '@/utils/domain/facies/local'
import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import CrossSection from '@/utils/domain/gaussianRandomField/crossSection'
import Region from '@/utils/domain/region'
import { ID, Identified } from '@/utils/domain/types'
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
}

interface RootState {
  _loaded: boolean
  _loading: {
    value: boolean
    message: string
  }

  gridModels: GridModelsState

  gaussianRandomFields: {
    fields: Identified<GaussianRandomField>
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

  parameters: {
    probabilityCube: {
      available: string[]
    }
  }

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
  'faciesTable': Facies[]

  'facies/byId': (faciesId: ID) => Facies | null
  'facies/selected': Facies[]
  'facies/constantProbability': (parent?: Parent) => boolean
  'facies/availableForBackgroundFacies': (rule: TruncationRuleBase<Polygon>, facies: Facies) => boolean

  'facies/global/selected': GlobalFacies[]

  'facies/groups/used': (facies: Facies) => boolean

  'fields': GaussianRandomField[]

  'truncationRule': TruncationRule
  'truncationRules/typeById': (id: ID) => string | null

  'gaussianRandomFields/crossSections/current': CrossSection

  options: {
    filterZeroProbability: boolean
  }
  'region': Region
  'zone': Zone
}

export {
  Store,
  RootState,
  RootGetters,
  Context,
}

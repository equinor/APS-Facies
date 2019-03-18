import { Parent } from '@/utils/domain/bases/interfaces'
import GlobalFacies from '@/utils/domain/facies/global'
import Facies from '@/utils/domain/facies/local'
import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import CrossSection from '@/utils/domain/gaussianRandomField/crossSection'
import { ID, Identified } from '@/utils/domain/types'

interface Store {
  state: RootState
  getters: RootGetters
}

interface RootState {
  facies: {
    available: Identified<Facies>
  }
}

interface RootGetters {
  'faciesTable': Facies[]

  'facies/byId': (faciesId: ID) => Facies
  'facies/selected': Facies[]
  'facies/constantProbability': (parent?: Parent) => boolean

  'facies/global/selected': GlobalFacies[]

  'facies/groups/used': (facies: Facies) => boolean

  'fields': GaussianRandomField[]

  'truncationRules/typeById': (id: ID) => string | null

  'gaussianRandomFields/crossSections/current': CrossSection

  options: {
    filterZeroProbability: boolean
  }
}

export {
  Store,
  RootState,
  RootGetters,
}

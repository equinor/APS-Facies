import { DEFAULT_FACIES_AUTOFILL } from '@/config'
import { makeOption } from '@/store/utils'

import showNameOrNumber from './nameNumber'
import automaticAlphaFieldSelection from './alphaChannels'

const filterZeroProbability = makeOption(false, [true, false])

export default {
  namespaced: true,
  modules: {
    showNameOrNumber,
    automaticAlphaFieldSelection,
    filterZeroProbability,
    automaticFaciesFill: makeOption(DEFAULT_FACIES_AUTOFILL, [true, false]),
  },
}

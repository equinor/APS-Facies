import { DEFAULT_FACIES_AUTOFILL } from '@/config'
import { makeOption } from '@/store/utils'

import { Module } from 'vuex'
import OptionsState from '@/store/modules/options/typing'
import { RootState } from '@/store/typing'

import showNameOrNumber from './nameNumber'
import automaticAlphaFieldSelection from './alphaChannels'

const filterZeroProbability = makeOption(false, [true, false])

const module: Module<OptionsState, RootState> = {
  namespaced: true,

  modules: {
    showNameOrNumber,
    automaticAlphaFieldSelection,
    filterZeroProbability,
    automaticFaciesFill: makeOption(DEFAULT_FACIES_AUTOFILL, [true, false]),
  },
}

export default module

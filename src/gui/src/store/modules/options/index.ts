import {
  COLOR_SCALES,
  DEFAULT_COLOR_SCALE,
  DEFAULT_FACIES_AUTOFILL,
  DEFAULT_IMPORT_FIELDS_IN_FMU,
} from '@/config'
import { makeOption, populateState } from '@/store/utils'

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
    colorScale: makeOption(DEFAULT_COLOR_SCALE, COLOR_SCALES),
    importFields: makeOption(DEFAULT_IMPORT_FIELDS_IN_FMU, [true, false]),
  },

  actions: {
    async populate (context, options): Promise<void> {
      await populateState(context, options)
    },
  },
}

export default module

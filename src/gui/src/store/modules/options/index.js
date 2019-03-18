import { makeOption } from '@/store/utils'

import showNameOrNumber from './nameNumber'
import automaticAlphaFieldSelection from './alphaChannels'

const filterZeroProbability = makeOption(false, [true, false])

export default {
  namespaced: true,

  state: {},

  modules: {
    showNameOrNumber,
    automaticAlphaFieldSelection,
    filterZeroProbability,
    automaticFill: makeOption(true, [true, false])
  },

  actions: {},

  mutations: {},

  getters: {},
}

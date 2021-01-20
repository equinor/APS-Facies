import { Module } from 'vuex'
import { RootState } from '@/store/typing'
import { makeOption, populateState } from '@/store/utils'

const item = makeOption('number', ['number', 'name'])

const module: Module<{}, RootState> = {
  namespaced: true,
  modules: {
    zone: item,
    region: item,
  },

  actions: {
    async populate (context, options): Promise<void> {
      await populateState(context, options)
    },
  },
}

export default module

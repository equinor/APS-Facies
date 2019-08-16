import { Module } from 'vuex'
import { RootState } from '@/store/typing'
import { makeOption } from '@/store/utils'

const item = makeOption('number', ['number', 'name'])

const module: Module<{}, RootState> = {
  namespaced: true,
  modules: {
    zone: item,
    region: item,
  },

  actions: {
    async populate ({ dispatch }, options): Promise<void> {
      await Promise.all(Object.keys(options)
        .map(option => dispatch(`${option}/populate`, options[`${option}`]))
      )
    },
  },
}

export default module

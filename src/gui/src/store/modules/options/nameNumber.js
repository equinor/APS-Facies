import { makeOption } from '@/store/utils'

const item = makeOption('number', ['number', 'name'])

export default {
  namespaced: true,
  state: {
  },
  modules: {
    zone: item,
    region: item,
  },
  actions: {},
  mutations: {},
  getters: {},
}

import region from '@/store/modules/parameters/region'
import blockedWell from '@/store/modules/parameters/blockedWell'
import blockedWellLog from '@/store/modules/parameters/blockedWellLog'
import rmsTrend from '@/store/modules/parameters/rmsTrend'
import probabilityCube from '@/store/modules/parameters/probabilityCube'

export default {
  namespaced: true,
  state: {},
  modules: {
    region,
    blockedWell,
    blockedWellLog,
    rmsTrend,
    probabilityCube,
  },
  actions: {},
  mutations: {},
  getters: {},
}

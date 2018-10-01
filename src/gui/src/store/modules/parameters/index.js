import zone from '@/store/modules/parameters/zone'
import region from '@/store/modules/parameters/region'
import blockedWell from '@/store/modules/parameters/blockedWell'
import blockedWellLog from '@/store/modules/parameters/blockedWellLog'
import rmsTrend from '@/store/modules/parameters/rmsTrend'

export default {
  namespaced: true,
  state: {},
  modules: {
    zone,
    region,
    blockedWell,
    blockedWellLog,
    rmsTrend,
  },
  actions: {},
  mutations: {},
  getters: {},
}

import region from '@/store/modules/parameters/region'
import blockedWell from '@/store/modules/parameters/blockedWell'
import blockedWellLog from '@/store/modules/parameters/blockedWellLog'
import rmsTrend from '@/store/modules/parameters/rmsTrend'
import probabilityCube from '@/store/modules/parameters/probabilityCube'
import grid from '@/store/modules/parameters/grid'

export default {
  namespaced: true,
  state: {},
  modules: {
    region,
    blockedWell,
    blockedWellLog,
    rmsTrend,
    probabilityCube,
    grid,
  },
  actions: {},
  mutations: {},
  getters: {},
}

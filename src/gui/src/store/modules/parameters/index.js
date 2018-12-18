import zone from '@/store/modules/parameters/zone'
import region from '@/store/modules/parameters/region'
import blockedWell from '@/store/modules/parameters/blockedWell'
import blockedWellLog from '@/store/modules/parameters/blockedWellLog'
import rmsTrend from '@/store/modules/parameters/rmsTrend'
import probabilityCube from '@/store/modules/parameters/probabilityCube'
import grid from '@/store/modules/parameters/grid'
import realization from '@/store/modules/parameters/realization'
import path from '@/store/modules/parameters/path'
import names from '@/store/modules/parameters/names'

export default {
  namespaced: true,
  state: {},
  modules: {
    zone,
    region,
    blockedWell,
    blockedWellLog,
    rmsTrend,
    probabilityCube,
    grid,
    realization,
    path,
    names,
  },
  actions: {},
  mutations: {},
  getters: {},
}

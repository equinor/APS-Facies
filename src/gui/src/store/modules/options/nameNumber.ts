import { makeOption } from '@/store/utils'

const item = makeOption('number', ['number', 'name'])

export default {
  namespaced: true,
  modules: {
    zone: item,
    region: item,
  },
}

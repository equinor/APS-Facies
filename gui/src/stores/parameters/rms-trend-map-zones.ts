import { acceptHMRUpdate, defineStore } from 'pinia'
import rms from '@/api/rms'
import type { Ref } from 'vue'
import { ref } from 'vue'

export interface TrendMap {
  name: string
  representations: string[]
}

export const useParameterRmsTrendMapZoneStore = defineStore(
  'parameters-rms-trend-map-zones',
  () => {
    const available = ref([]) as Ref<TrendMap[]>

    async function refresh() {
      const zoneRepresentations = await rms.trendMapZones()
      available.value = Object.entries(zoneRepresentations).map(
        ([name, representations]) => ({ name, representations }),
      )
    }
    const fetch = refresh // alias

    function $reset() {
      available.value = []
    }

    return { available, fetch, refresh, $reset }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterRmsTrendMapZoneStore, import.meta.hot),
  )
}

import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import rms from '@/api/rms'

function defineOptionsStore(id: string) {
  return defineStore(id, () => {
    const available = ref<string[]>([])

    async function fetch(type: string) {
      available.value = await rms.options(type)
    }
    return { available, fetch }
  })
}

export const useConstantsOptionsVariogramsStore = defineOptionsStore(
  'constants-options-variograms',
)
export const useConstantsOptionsOriginStore = defineOptionsStore(
  'constants-options-origin',
)
export const useConstantsOptionsStackingStore = defineOptionsStore(
  'constants-options-stacking',
)
export const useConstantsOptionsTrendsStore = defineOptionsStore(
  'constants-options-trends',
)

export const useConstantsOptionsStore = defineStore('constants-options', () => {
  async function fetch() {
    const variogramsStore = useConstantsOptionsVariogramsStore()
    const originStore = useConstantsOptionsOriginStore()
    const stackingStore = useConstantsOptionsStackingStore()
    const trendsStore = useConstantsOptionsTrendsStore()
    await Promise.all([
      variogramsStore.fetch('variogram'),
      originStore.fetch('origin'),
      stackingStore.fetch('stacking_direction'),
      trendsStore.fetch('trend'),
    ])
  }

  return { fetch }
})

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsOptionsVariogramsStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsOptionsOriginStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsOptionsStackingStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsOptionsTrendsStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsOptionsStore, import.meta.hot),
  )
}

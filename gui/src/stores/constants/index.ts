import { acceptHMRUpdate, defineStore } from 'pinia'
import { useConstantsRangesStore } from './ranges'
import { useConstantsOptionsStore } from './options'
import { useConstantsGaussianRandomFieldsStore } from './gaussian-random-fields'
import { useConstantsFaciesColorsStore } from './facies-colors'
import type { ColorLibrarySerialization } from '@/utils/domain/colorLibrary'
import type { CurrentIdentifiedStoreSerialization } from '@/stores/utils/identified-items'

export const useConstantsStore = defineStore('constants', () => {
  async function fetch() {
    const rangesStore = useConstantsRangesStore()
    const optionsStore = useConstantsOptionsStore()
    const faciesColorsStore = useConstantsFaciesColorsStore()
    const gaussianRandomFieldStore = useConstantsGaussianRandomFieldsStore()
    await Promise.all([
      rangesStore.fetch(),
      optionsStore.fetch(),
      faciesColorsStore.fetch(),
      gaussianRandomFieldStore.fetch(),
    ])
  }

  return { fetch }
})

export interface ConstantStoreSerialization {
  faciesColors: CurrentIdentifiedStoreSerialization<ColorLibrarySerialization>
}
export function useConstantStoreSerialization(): ConstantStoreSerialization {
  const faciesColorsStore = useConstantsFaciesColorsStore()
  return {
    faciesColors: {
      available: faciesColorsStore.available.map((library) => library.toJSON()),
      current: faciesColorsStore.currentId,
    },
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useConstantsStore, import.meta.hot))
}

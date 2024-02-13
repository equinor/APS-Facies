import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'

const DEFAULT_MIN = 2
const NUMBER_BAYFILL = 3

function defineResettableRangeStore(
  id: string,
  defaultMin: number,
  defaultMax: number,
) {
  return defineStore(id, () => {
    const min = ref<number | null>(null)
    const max = ref<number | null>(null)

    function fetch() {
      // this "fetch" is actually more of a "reset"-function, but we
      // try to use the same API for all these constants-stores.
      min.value = defaultMin
      max.value = defaultMax
    }
    return { min, max, fetch }
  })
}

export const useConstantsGaussianRandomFieldsCubicStore =
  defineResettableRangeStore(
    'constants-gaussian-random-fields-cubic',
    DEFAULT_MIN,
    Number.POSITIVE_INFINITY,
  )
export const useConstantsGaussianRandomFieldsNonCubicStore =
  defineResettableRangeStore(
    'constants-gaussian-random-fields-non-cubic',
    DEFAULT_MIN,
    Number.POSITIVE_INFINITY,
  )
export const useConstantsGaussianRandomFieldsBayfillStore =
  defineResettableRangeStore(
    'constants-gaussian-random-fields-bayfill',
    NUMBER_BAYFILL,
    NUMBER_BAYFILL,
  )

export const useConstantsGaussianRandomFieldsStore = defineStore(
  'constants-gaussian-random-fields',
  () => {
    function fetch() {
      const cubic = useConstantsGaussianRandomFieldsCubicStore()
      const nonCubic = useConstantsGaussianRandomFieldsNonCubicStore()
      const bayfill = useConstantsGaussianRandomFieldsBayfillStore()
      cubic.fetch()
      nonCubic.fetch()
      bayfill.fetch()
    }

    return { fetch }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(
      useConstantsGaussianRandomFieldsCubicStore,
      import.meta.hot,
    ),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(
      useConstantsGaussianRandomFieldsNonCubicStore,
      import.meta.hot,
    ),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(
      useConstantsGaussianRandomFieldsBayfillStore,
      import.meta.hot,
    ),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsGaussianRandomFieldsStore, import.meta.hot),
  )
}

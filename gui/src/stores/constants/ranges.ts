import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, ref } from 'vue'
import rms from '@/api/rms'

function defineRangedStore(id: string) {
  return defineStore(id, () => {
    const min = ref<number | null>(null)
    const max = ref<number | null>(null)

    const minMax = computed(() => ({
      min: min.value ?? -Infinity,
      max: max.value ?? Infinity,
    }))

    async function fetch(type: string) {
      const response = await rms.constants(type, 'min,max')
      min.value = response.min
      max.value = response.max
    }
    return { min, max, minMax, fetch }
  })
}

export const useConstantsRangesAzimuthStore = defineRangedStore(
  'constants-ranges-azimuth',
)
export const useConstantsRangesDipStore = defineRangedStore(
  'constants-ranges-dip',
)
export const useConstantsRangesPowerStore = defineRangedStore(
  'constants-ranges-power',
)
export const useConstantsRangesDepositionalAzimuthStore = defineRangedStore(
  'constants-ranges-depositional-azimuth',
)
export const useConstantsRangesStackingStore = defineRangedStore(
  'constants-ranges-stacking',
)
export const useConstantsRangesMigrationStore = defineRangedStore(
  'constants-ranges-migration',
)

export const useConstantsRangesStore = defineStore('constants-ranges', () => {
  async function fetch() {
    const azimuthStore = useConstantsRangesAzimuthStore()
    const dipStore = useConstantsRangesDipStore()
    const powerStore = useConstantsRangesPowerStore()
    const depositionalAzimuthStore =
      useConstantsRangesDepositionalAzimuthStore()
    const stackingStore = useConstantsRangesStackingStore()
    const migrationStore = useConstantsRangesMigrationStore()
    await Promise.all([
      azimuthStore.fetch('azimuth'),
      dipStore.fetch('dip'),
      powerStore.fetch('power'),
      depositionalAzimuthStore.fetch('depositional_direction'),
      stackingStore.fetch('stacking_angle'),
      migrationStore.fetch('migration_angle'),
    ])
  }

  return { fetch }
})

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsRangesAzimuthStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsRangesDipStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsRangesPowerStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(
      useConstantsRangesDepositionalAzimuthStore,
      import.meta.hot,
    ),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsRangesStackingStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsRangesMigrationStore, import.meta.hot),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsRangesStore, import.meta.hot),
  )
}

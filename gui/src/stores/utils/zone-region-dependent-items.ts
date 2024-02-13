import type { ZoneRegionDependent } from '@/utils/domain/bases'
import { useZoneStore } from '@/stores/zones'
import type { WritableComputedRef } from 'vue'
import { computed, ref } from 'vue'
import { hasParents } from '@/utils'
import type { IdentifiedItems } from '@/stores/utils/identified-items'
import { useIdentifiedItems } from '@/stores/utils/identified-items'
import { useRegionStore } from '@/stores/regions'
import type { Region, Zone } from '@/utils/domain'

interface ZoneRegionDependentItems<T extends ZoneRegionDependent> extends IdentifiedItems<T> {
  current: WritableComputedRef<T | null>
}

export function useZoneRegionDependentStore<T extends ZoneRegionDependent>(): ZoneRegionDependentItems<T> {
  const store = useIdentifiedItems<T>()
  const { available } = store

  const { current: currentZone } = useZoneStore()
  const { current: currentRegion } = useRegionStore()

  const currentId = ref<string | null>(null)
  const current = computed<T | null>({
    get: () => {
      if (!currentZone) return null;

      const relevant = available.value.filter(item => hasParents(item, currentZone as Zone, currentRegion as Region))
      if (relevant.length === 0) return relevant[0]
      return relevant.find(({ id }) => id === currentId.value) ?? null
    },
      set: (value: T | null) => {
        currentId.value = value?.id ?? null
    }
})

  function $reset() {
    store.$reset()
    currentId.value = null
  }


  return {
    ...store,
    current,
    $reset,
  }
}

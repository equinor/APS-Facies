import type { ComputedRef, Ref } from 'vue'
import { computed, ref } from 'vue'
import { identify } from '@/utils'
import type { Identifiable, Identified } from '@/utils/domain/bases/interfaces'
import type { ID } from '@/utils/domain/types'

export type IdentifiedStorePopulationData<T> = {
  available: T[]
}
export type CurrentIdentifiedStorePopulationData<T> =
  IdentifiedStorePopulationData<T> & {
    current?: T
  }

export type IdentifiedItems<T extends Identifiable> = {
  available: Ref<T[]>
  identifiedAvailable: ComputedRef<Identified<T>>
  addAvailable: (item: T) => void
  removeAvailable: (item: T) => void
  $reset: () => void
}

export type CurrentIdentifiedItems<T extends Identifiable> = IdentifiedItems<T> & {
  currentId: Ref<ID | null>
  current: ComputedRef<T | null>
}

export function useIdentifiedItems<
  T extends Identifiable,
>(): IdentifiedItems<T> {
  const available = ref([]) as Ref<T[]>
  const identifiedAvailable = computed(() => identify(available.value))

  function addAvailable(item: T) {
    available.value.push(item)
  }

  function removeAvailable(item: T) {
    const index = available.value.findIndex((i) => i.id === item.id)
    if (index === -1) {
      console.warn("Can't remove item not found in available-list:", item)
    } else {
      available.value.splice(index, 1)
    }
  }

  function $reset() {
    available.value = []
  }

  return {
    available,
    identifiedAvailable,
    addAvailable,
    removeAvailable,
    $reset,
  }
}

export function useCurrentIdentifiedItems<
  T extends Identifiable,
>(): CurrentIdentifiedItems<T> {
  const availableStore = useIdentifiedItems<T>()
  const { available, identifiedAvailable, addAvailable, removeAvailable } = availableStore

  const currentId = ref<ID | null>(null)
  const current = computed(() => {
    if (!currentId.value) return null
    return identifiedAvailable.value[currentId.value] ?? null
  })

  function $reset() {
    availableStore.$reset()
    currentId.value = null
  }

  return {
    available,
    identifiedAvailable,
    addAvailable,
    removeAvailable,
    currentId,
    current,
    $reset,
  }
}

export interface CurrentIdentifiedStoreSerialization<T extends Identifiable> {
  available: T[]
  current: ID | null
}


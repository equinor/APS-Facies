import type { Ref } from 'vue'
import { ref } from 'vue'

export function useSelectableChoice<T>() {
  const available = ref([]) as Ref<T[]>
  const selected = ref<T | null>(null)

  function $reset() {
    available.value = []
    selected.value = null
  }

  return { available, selected, $reset }
}

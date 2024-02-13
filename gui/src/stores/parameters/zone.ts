import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'

export const useParameterZoneStore = defineStore('parameter-zone', () => {
  const selected = ref<string | null>(null)

  function select(zone: string) {
    selected.value = zone
  }

  function $reset() {
    selected.value = null
  }

  return { selected, select, $reset }
})

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterZoneStore, import.meta.hot),
  )
}

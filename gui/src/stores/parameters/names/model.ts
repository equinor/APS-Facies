import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'

export const useParameterNameModelStore = defineStore(
  'parameter-name-model',
  () => {
    const selected = ref<string | null>(null)

    function select(name: string) {
      selected.value = name
    }

    function $reset() {
      selected.value = null
    }

    return { selected, select, $reset }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterNameModelStore, import.meta.hot),
  )
}

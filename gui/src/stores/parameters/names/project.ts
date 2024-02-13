import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import rms from '@/api/rms'

export const useParameterNameProjectStore = defineStore(
  'parameter-name-project',
  () => {
    const selected = ref<string | null>(null)

    function select(name: string) {
      selected.value = name
    }

    async function fetch() {
      const currentProjectName = await rms.projectName()
      select(currentProjectName)
    }

    function $reset() {
      selected.value = null
    }

    return { selected, select, fetch, $reset }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterNameProjectStore, import.meta.hot),
  )
}

import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import rms from '@/api/rms'

export const useParameterNameWorkflowStore = defineStore(
  'parameter-name-workflow',
  () => {
    const selected = ref<string | null>(null)

    function select(name: string) {
      selected.value = name
    }

    async function fetch() {
      const currentWorkflowName = await rms.currentWorkflowName()
      select(currentWorkflowName)
    }

    function $reset() {
      selected.value = null
    }

    return { selected, select, fetch, $reset }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterNameWorkflowStore, import.meta.hot),
  )
}

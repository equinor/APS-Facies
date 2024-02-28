import { acceptHMRUpdate, defineStore } from 'pinia'
import { createModel } from '@/utils/helpers/processing/export'
import { computed } from 'vue'

export const useModelFileExporterStore = defineStore(
  'model-file-exporter',
  () => {
    async function createModelFileFromStore(includeAuxiliaryData = false): Promise<string> {
      return new Promise((resolve, reject) => {
        try {
          const xmlString = createModel(includeAuxiliaryData)
          resolve(xmlString)
        } catch (error) {
          reject(error)
        }
      })
    }

    const model = computed(() => {
      try {
        return btoa(createModel())
      } catch (e) {}
      return ''
    })

    return { model, createModelFileFromStore }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useModelFileExporterStore, import.meta.hot),
  )
}

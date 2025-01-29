import { useRootStore } from '@/stores'
import { useGridModelStore } from '@/stores/grid-models'
import { dumpState } from '@/utils/helpers/processing/export'

interface SerializedState {
  [_: string]: any
}

export interface RmsJob extends SerializedState {
  _treeorigin: string
  _version: string
}

export function attachRMSListeners() {
  if (typeof rms !== 'undefined') {
    rms.onPluginSave((): SerializedState => {
      return dumpState()
    })

    rms.onPluginLoaded(async (data: RmsJob): Promise<void> => {
      // NOTE: an 'empty' data object from RMS, looks like this:
      // { _treeorigin: "", _version: "1.2" }
      const rootStore = useRootStore()
      if (Object.keys(data).length > 2) {
        await rootStore.populate(data)
      } else {
        const match = /^Grid models\/(.*)$/g.exec(data._treeorigin)
        if (match) {
          let gridModel = match[1]
          // The resulting output may include a nested path (/-separated), while a grid model MAY have the '/' character
          const { available, select } = useGridModelStore()
          const gridModelNames = available.map((model) => model.name)
          for (const model of gridModelNames) {
            if (gridModel.includes(model)) {
              gridModel = model
              break
            }
          }
          if (gridModel) {
            await select(gridModel)
          }
        }
      }
    })
  }
}

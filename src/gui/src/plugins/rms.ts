/* eslint-disable no-undef */
/* eslint-disable @typescript-eslint/ban-ts-ignore */
import { debounce } from 'lodash'
import store from '@/store'

import { dumpState } from '@/utils/helpers/processing/export'

interface SerializedState {
  [_: string]: any
}

interface RmsJob extends SerializedState {
  _treeorigin: string
  _version: string
  [_: string]: any
}

// @ts-ignore
if (typeof rms !== 'undefined') {
  // @ts-ignore
  rms.onPluginSave((): SerializedState => {
    return dumpState(store)
  })

  // @ts-ignore
  rms.onPluginLoaded((data: RmsJob): void => {
    // NOTE: an 'empty' data object from RMS, looks like this:
    // { _treeorigin: "", _version: "1.2" }
    // TODO: Handle different versions, (and merge?)
    if (Object.keys(data).length > 2) {
      store.dispatch('populate', data)
    } else {
      const match = /^Grid models\/(.*)$/g.exec(data._treeorigin)
      if (match) {
        let gridModel = match[1]
        // The resulting output may include a nested path (/-separated), while a grid model MAY have the '/' character
        for (const model of store.getters.gridModels) {
          if (gridModel.includes(model)) {
            gridModel = model
            break
          }
        }
        if (gridModel) {
          store.dispatch('gridModels/select', gridModel)
        }
      }
    }
  })

  const changes: { name: string, action: () => Promise<void> }[] = [
    {
      name: 'Grid models',
      action: (): Promise<void> => store.dispatch(
        'refresh',
        'Detected one, or more changes in RMS\' grid models, or their parameters.\nThe GUI refreshes.',
      ),
    },
  ]

  const onProjectChanged = debounce(
    async (what: string[]): Promise<void> => {
      await Promise.all(changes
        .filter(({ name }) => what.includes(name))
        .map(({ action }) => action())
      )
    },
    2000,
    {
      trailing: true,
    }
  )

  // @ts-ignore
  rms.onProjectChanged(onProjectChanged)
}

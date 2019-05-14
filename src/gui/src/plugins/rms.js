/* eslint-disable no-undef */
import store from '@/store'

if (typeof rms !== 'undefined') {
  rms.onPluginSave(() => {
    return store.state
  })

  rms.onPluginLoaded(data => {
    // NOTE: an 'empty' data object from RMS, looks like this:
    // { _treeorigin: "", _version: "1.2" }
    // TODO: Handle different versions, (and merge?)
    if (Object.keys(data).length > 2) {
      store.dispatch('populate', data)
    } else {
      let gridModel = /^Grid models\/(.*)$/g.exec(data['_treeorigin'])[1]
      // The resulting output may include a nested path (/-separated), while a grid model MAY have the '/' character
      for (const model of store.state.gridModels.available) {
        if (gridModel.includes(model)) {
          gridModel = model
          break
        }
      }
      if (gridModel) {
        store.dispatch('gridModels/select', gridModel)
      }
    }
  })
}

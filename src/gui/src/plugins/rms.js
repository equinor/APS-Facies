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
    store.dispatch('populate', data)
  })
}

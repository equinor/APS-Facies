import Vue from 'vue'

export const SELECTED_ITEMS = (state, { id, toggled }) => {
  state.available[`${id}`].selected = toggled
}

export const ADD_ITEM = (state, { id, item }) => {
  Vue.set(state, id, item)
}
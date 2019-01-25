import Vue from 'vue'

export const SELECTED_ITEMS = (state, { id, toggled }) => {
  Vue.set(state.available[`${id}`], 'selected', toggled)
}

export const ADD_ITEM = (state, { id, item }) => {
  Vue.set(state, id, item)
}

export const AVAILABLE = (state, items) => {
  Vue.set(state, 'available', items)
}

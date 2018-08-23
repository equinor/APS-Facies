export const SELECTED_ITEMS = (state, {id, toggled}) => {
  state.available[`${id}`].selected = toggled
}

import uuidv4 from 'uuid/v4'

export const addItem = ({ commit }, { item }) => {
  // TODO: Checks field is valid / migrate to typescript
  const id = item.id || uuidv4()
  commit('ADD', { id, item })
  return new Promise((resolve, reject) => {
    resolve(id)
  })
}

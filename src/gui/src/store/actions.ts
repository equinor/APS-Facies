import uuidv4 from 'uuid/v4'

function addItem ({ commit }: { commit: (name: string, value: any) => void}, { item }: { item: any}): Promise<any> {
  // TODO: Checks field is valid / migrate to typescript
  const id = item.id || uuidv4()
  commit('ADD', { id, item })
  return new Promise((resolve, reject) => {
    resolve(item)
  })
}

export {
  addItem,
}

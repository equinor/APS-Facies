import uuidv4 from 'uuid/v4'
import { Polygon, TruncationRule } from '@/utils/domain'
import { Dispatch } from 'vuex'

function addItem ({ commit }: { commit: (name: string, value: any) => void}, { item }: { item: any}): Promise<any> {
  // TODO: Checks field is valid / migrate to typescript
  const id = item.id || uuidv4()
  commit('ADD', { id, item })
  return new Promise((resolve, reject) => {
    resolve(item)
  })
}

function updateFactor<S, G> (
  { dispatch }: { dispatch: Dispatch},
  rule: TruncationRule,
  item: Polygon,
  value: number
): Promise<any> {
  return dispatch('truncationRules/changeProportionFactors', { rule, polygon: item, value }, { root: true })
}

export {
  addItem,
  updateFactor,
}

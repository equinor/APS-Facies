import { acceptHMRUpdate, defineStore } from 'pinia'
import { truncationRules } from '.'
import { ref } from 'vue'

import type { TruncationRuleType } from '@/utils/domain/truncationRule/base'
import type { PolygonSerialization } from '@/utils/domain/polygon/base'

export interface TruncationRuleTemplateType {
  name: string
  type: TruncationRuleType
  order: number
  polygons?: PolygonSerialization[]
}

function _equal(
  first: TruncationRuleTemplateType[],
  second: TruncationRuleTemplateType[],
) {
  return (
    first.length === second.length &&
    first.every(
      (rule1) =>
        second.find(
          (rule2) => rule1.name === rule2.name && rule1.type === rule2.type,
        ) !== undefined,
    )
  )
}

export const useTruncationRuleTemplateTypeStore = defineStore(
  'truncation-rule-template-types',
  () => {
    const available = ref<TruncationRuleTemplateType[]>([])

    function fetch() {
      available.value = [...truncationRules.types]
    }

    function populate(types: TruncationRuleTemplateType[]) {
      if (!_equal(types, truncationRules.types)) {
        // if we're verifying that the given types-array is equal to our pre-existing
        // templates.types array... why even accept a types array?
        throw new Error(
          'NOT IMPLEMENTED: The given types to not match the types given in the templates',
        )
      }
      available.value = types
    }

    return {
      available,
      fetch,
      populate,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useTruncationRuleTemplateTypeStore, import.meta.hot),
  )
}

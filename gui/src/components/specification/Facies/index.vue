<template>
  <facies-specification-base
    :model-value="value.facies"
    :disable="disable"
    :clearable="clearable"
    @update:model-value="(facies) => updateFacies(facies)"
  />
</template>

<script
  setup
  lang="ts"
  generic="T extends Polygon,
  RULE extends InstantiatedTruncationRule
"
>
import type Facies from '@/utils/domain/facies/local'
import type Polygon from '@/utils/domain/polygon/base'
import type { InstantiatedTruncationRule } from '@/utils/domain'

import FaciesSpecificationBase from './base.vue'
import { useStore } from '../../../store'

type Props = {
  value: T
  rule: RULE
  clearable?: boolean
  disable?: boolean | ((facies: Facies) => boolean)
}
const props = withDefaults(defineProps<Props>(), {
  clearable: false,
  disable: false,
})
const store = useStore()

async function updateFacies(faciesId: ID | undefined): Promise<void> {
  const facies = store.getters['facies/byId'](faciesId)
  await store.dispatch('truncationRules/updateFacies', {
    rule: props.rule,
    polygon: props.value,
    facies,
  })
}
</script>

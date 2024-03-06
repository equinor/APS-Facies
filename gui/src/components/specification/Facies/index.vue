<template>
  <facies-specification-base
    v-model="facies"
    :disable="disable"
    :clearable="clearable"
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
import { computed } from 'vue'
import { useTruncationRuleStore } from '@/stores/truncation-rules'

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

const ruleStore = useTruncationRuleStore()

const facies = computed({
  get: () => props.value.facies,
  set: (value: Facies | null) => (value ? updateFacies(value) : undefined),
})

function updateFacies(facies: Facies): void {
  ruleStore.updateFacies(props.rule, props.value, facies)
}
</script>

<template>
  <facies-specification
    :value="value"
    :rule="rule"
    :disable="(facies) => overlayFacies(facies)"
  />
</template>

<script setup lang="ts">
import FaciesSpecification from '@/components/specification/Facies/index.vue'

import { Bayfill, Facies, Polygon, TruncationRule } from '@/utils/domain'

type Props = {
  value: Polygon
  rule: TruncationRule
}
const props = defineProps<Props>()

function overlayFacies(facies: Facies): boolean {
  if (props.rule instanceof Bayfill) {
    return false
  }
  return props.rule.isUsedInOverlay(facies)
}
</script>

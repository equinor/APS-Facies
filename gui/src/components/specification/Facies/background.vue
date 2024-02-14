<template>
  <facies-specification
    :value="value"
    :rule="rule as InstantiatedTruncationRule"
    :disable="(facies) => overlayFacies(facies)"
  />
</template>

<script
  setup
  lang="ts"
  generic="T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends TruncationRule<T, S, P>
"
>
import FaciesSpecification from '@/components/specification/Facies/index.vue'

import type { Facies, InstantiatedTruncationRule, Polygon } from '@/utils/domain'
import type { TruncationRule } from '@/utils/domain/truncationRule'
import type { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import { isOverlayTruncationRule } from '@/utils/domain/truncationRule/helpers'

type Props = {
  value: Polygon
  rule: RULE
}
const props = defineProps<Props>()

function overlayFacies(facies: Facies): boolean {
  if (isOverlayTruncationRule(props.rule)) {
    return props.rule.isUsedInOverlay(facies)
  }
  return false
}
</script>

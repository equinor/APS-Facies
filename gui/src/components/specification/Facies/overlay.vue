<template>
  <facies-specification
    :value="value"
    :rule="rule as InstantiatedOverlayTruncationRule"
    :disable="(facies) => backgroundFacies(facies)"
  />
</template>

<script
  setup
  lang="ts"
  generic="
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends OverlayTruncationRule<T, S, P>
  "
>
import FaciesSpecification from '@/components/specification/Facies/index.vue'

import type {
  InstantiatedOverlayTruncationRule,
  OverlayPolygon,
  Polygon,
  Facies,
} from '@/utils/domain'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

type Props = {
  value: OverlayPolygon
  rule: RULE
}
const props = defineProps<Props>()

function backgroundFacies(facies: Facies): boolean {
  return props.rule.isUsedInBackground(facies)
}
</script>

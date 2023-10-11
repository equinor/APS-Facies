<template>
  <facies-specification
    :value="value"
    :rule="rule"
    :disable="(facies) => backgroundFacies(facies)"
  />
</template>

<script
  setup
  lang="ts"
  generic="
    T extends Polygon = Polygon,
    S extends PolygonSerialization = PolygonSerialization,
    P extends PolygonSpecification = PolygonSpecification,
"
>
import FaciesSpecification from '@/components/specification/Facies/index.vue'

import { OverlayPolygon, Polygon, Facies } from '@/utils/domain'
import {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

type Props = {
  value: OverlayPolygon
  rule: OverlayTruncationRule<T, S, P>
}
const props = defineProps<Props>()

function backgroundFacies(facies: Facies): boolean {
  return props.rule.isUsedInBackground(facies)
}
</script>

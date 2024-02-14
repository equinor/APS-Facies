<template>
  <fraction-field
    :model-value="props.value.fraction"
    :append-icon="appendIcon"
    :disabled="disabled"
    @update:model-value="(fraction) => updateFactor(props.value, fraction as number)"
    @click:append="normalizeFractions()"
  />
</template>

<script
  setup
  lang="ts"
  generic="T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends TruncationRule<T, S, P> | InstantiatedTruncationRule
"
>
import FractionField from '@/components/selection/FractionField.vue'

import type {
  Polygon,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type TruncationRule from '@/utils/domain/truncationRule/base'

import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { getId } from '@/utils'
import { computed } from 'vue'
import vuetify from '@/plugins/vuetify'
import type { InstantiatedTruncationRule } from '@/utils/domain'

const props = defineProps<{
  value: T
  rule: RULE
}>()

const disabled = computed(() => {
  return (
    !hasFaciesSpecifiedForMultiplePolygons(
      props.rule.polygons,
      props.value.facies,
    ) || !props.value.facies
  )
})

// type: VuetifyIcon
const appendIcon = computed(() => {
  return disabled.value || props.rule.isPolygonFractionsNormalized(props.value)
    ? ''
    : vuetify.icons.aliases.refresh
})

function updateFactor(polygon: T, value: number): void {
  polygon.fraction = value
}

async function normalizeFractions(): Promise<void> {
  const polygons = props.rule.polygons.filter(
    (polygon): boolean =>
      getId(polygon.facies) === getId(props.value.facies),
  )
  const sum = polygons.reduce(
    (sum, polygon): number => polygon.fraction + sum,
    0,
  )
  await Promise.all(
    (polygons as T[]).map((polygon) => updateFactor(polygon, polygon.fraction / sum)),
  )
}
</script>

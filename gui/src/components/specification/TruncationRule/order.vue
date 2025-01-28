<template>
  <base-polygon-order
    :can-increase="canIncrease"
    :can-decrease="canDecrease"
    :can-remove="canRemove"
    :can-add="canAdd"
    @input="(direction: number) => changeOrder(direction)"
    @add="addPolygon"
    @delete="deletePolygon"
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
import type {
  Polygon,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import { OverlayPolygon } from '@/utils/domain'

import BasePolygonOrder from '@/components/specification/PolygonOrder.vue'
import { computed } from 'vue'
import { useTruncationRuleStore } from '@/stores/truncation-rules'

const props = withDefaults(
  defineProps<{
    value: T
    rule: RULE
    overlay?: boolean
    minPolygons?: number
  }>(),
  {
    overlay: false,
    minPolygons: 0,
  },
)
const ruleStore = useTruncationRuleStore()

const polygons = computed(() =>
  props.rule.polygons.filter((polygon) => polygon.overlay === props.overlay),
)

const orders = computed(() => polygons.value.map(({ order }) => order))
const max = computed(() => Math.max(...orders.value))
const min = computed(() => Math.min(...orders.value))

const hasMultiplePolygons = computed(() => polygons.value.length > 1)
const canIncrease = computed(
  () => hasMultiplePolygons.value && props.value.order < max.value,
)
const canDecrease = computed(
  () => hasMultiplePolygons.value && props.value.order > min.value,
)

const canAdd = computed(() => true)
const canRemove = computed(
  () =>
    (props.overlay && props.rule instanceof OverlayTruncationRule
      ? props.rule.overlayPolygons
      : props.rule.backgroundPolygons
    ).length > props.minPolygons,
)

function addPolygon(): void {
  ruleStore.addPolygon(props.rule, {
    order: props.value.order + 1,
    overlay: props.value.overlay,
    group:
      props.value instanceof OverlayPolygon ? props.value.group : undefined,
  })
}

function deletePolygon(): void {
  ruleStore.removePolygon(props.rule, props.value)
}

function changeOrder(direction: number): void {
  ruleStore.changeOrder(props.rule, props.value, direction)
}
</script>

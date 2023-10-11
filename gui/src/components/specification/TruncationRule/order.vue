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
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
"
>
import Polygon, {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import { OverlayPolygon } from '@/utils/domain'

import BasePolygonOrder from '@/components/specification/PolygonOrder.vue'
import { computed } from 'vue'
import { useStore } from '../../../store'

type Props = {
  value: T
  rule: TruncationRule<T, S, P>
  overlay?: boolean
  minPolygons?: number
}
const props = withDefaults(defineProps<Props>(), {
  overlay: false,
  minPolygons: 0,
})
const store = useStore()

const polygons = computed(() =>
  props.rule.polygons.filter((polygon) => polygon.overlay === props.overlay),
)
const orders = computed(() => polygons.value.map(({ order }) => order))

const hasMultiplePolygons = computed(() => polygons.value.length > 1)
const max = computed(() => Math.max(...orders.value))
const min = computed(() => Math.min(...orders.value))

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

async function addPolygon(): Promise<void> {
  await store.dispatch('truncationRules/addPolygon', {
    rule: props.rule,
    order: props.value.order + 1,
    overlay: props.value.overlay,
    group: props.value instanceof OverlayPolygon ? props.value.group : null,
  })
}

async function deletePolygon(): Promise<void> {
  await store.dispatch('truncationRules/removePolygon', {
    rule: props.rule,
    polygon: props.value,
  })
}

async function changeOrder(direction: number): Promise<void> {
  await store.dispatch('truncationRules/changeOrder', {
    rule: props.rule,
    polygon: props.value,
    direction,
  })
}
</script>

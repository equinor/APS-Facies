<template>
  <base-table
    :headers="headers"
    :items="polygons"
    :sort-by="[{ key: 'order', order: 'asc' }]"
    elevation="0"
    @input.stop
  >
    <template #item="{ item }">
      <tr>
        <td>
          <alpha-selection
            :value="item.field"
            :rule="props.rule"
            :group="item.group.id"
            hide-label
            @input="(field: string|null) => updateField(item, field!)"
          />
        </td>
        <td>
          <overlay-facies-specification :value="item" :rule="props.rule" />
        </td>
        <td v-if="needFraction">
          <polygon-fraction-field :value="item" :rule="props.rule as TruncationRule<T, S, P>" />
        </td>
        <td>
          <fraction-field
            :model-value="item.center"
            @update:model-value="(val: MaybeFmuUpdatable | null) => updateCenter(item, val)"
          />
        </td>
        <td>
          <polygon-order :value="item" :rule="props.rule as OverlayTruncationRule<T, S, P>" overlay />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script
  setup
  lang="ts"
  generic="T extends OverlayPolygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends OverlayTruncationRule<T, S, P> | InstantiatedOverlayTruncationRule
"
>
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import FractionField from '@/components/selection/FractionField.vue'
import PolygonFractionField from '@/components/selection/PolygonFractionField.vue'
import PolygonOrder from '@/components/specification/TruncationRule/order.vue'
import OverlayFaciesSpecification from '@/components/specification/Facies/overlay.vue'
import AlphaSelection from '@/components/specification/TruncationRule/AlphaSelection.vue'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import { TruncationRule } from '@/utils/domain/truncationRule'
import type { InstantiatedOverlayTruncationRule } from '@/utils/domain'
import BaseTable from '@/components/baseComponents/BaseTable.vue'
import type OverlayPolygon from '@/utils/domain/polygon/overlay'
import type { ID } from '@/utils/domain/types'
import type { HeaderItems } from '@/utils/typing'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { computed } from 'vue'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import type { MaybeFmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'

const props = defineProps<{
  value: T[]
  rule: RULE
}>()
const fieldStore = useGaussianRandomFieldStore()

const polygons = computed<T[]>(() => props.value)

const needFraction = computed(() =>
  hasFaciesSpecifiedForMultiplePolygons(props.rule.overlayPolygons),
)

const headers = computed<HeaderItems>(() => [
  {
    text: 'GRF',
    value: 'field',
    help: 'Gaussian Random Field',
  },
  {
    text: 'Overlay Facies',
    value: 'facies',
  },
  ...(needFraction.value
    ? [
        {
          text: 'Probability Fraction',
          value: 'fraction',
        },
      ]
    : []),
  {
    text: 'Center',
    value: 'center',
    help: 'Truncation Interval Center Point',
    /* or: The overlay facies will look more continuous if the value of the center point of
    the truncation interval is 0 or 1 and look more fragmented if a value between 0 and 1,
    typically 0.5 is chosen. */
  },
  {
    text: 'Order',
    value: 'order',
  },
])

function updateField(
  polygon: OverlayPolygon,
  fieldId: ID,
): void {
  const field = fieldStore.byId(fieldId)
  polygon.field = field ?? null
}

function updateCenter(
  polygon: OverlayPolygon,
  value: MaybeFmuUpdatable | null,
): void {
    if (value === null) {
      throw new Error('Cannot set center to be empty')
    }
    polygon.center = value
}
</script>

<style lang="scss" scoped>
th {
  white-space: normal;
  overflow-wrap: break-word;
}
</style>

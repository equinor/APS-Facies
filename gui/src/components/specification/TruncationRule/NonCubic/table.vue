<template>
  <base-table
    :value="polygons"
    :headers="headers"
    :items="polygons"
    :sort-by="[{ key: 'order', order: 'asc' }]"
    @input.stop
  >
    <template #item="{ item }">
      <tr>
        <td class="text-left">
          <numeric-field
            :model-value="item.angle"
            :ranges="{ min: -180.0, max: 180.0 }"
            :disabled="isLast(item)"
            fmu-updatable
            enforce-ranges
            allow-negative
            use-modulus
            unit="°"
            label=""
            @update:model-value="(angle) => updateAngle(item, angle)"
          />
        </td>
        <td class="text-left">
          <background-facies-specification :value="item" :rule="value" />
        </td>
        <td v-if="hasMultipleFaciesSpecified">
          <polygon-fraction-field :value="item" :rule="value" />
        </td>
        <td>
          <polygon-order :value="item" :rule="value" :min-polygons="2" />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script setup lang="ts">
import BaseTable from '@/components/baseComponents/BaseTable.vue'
import PolygonFractionField from '@/components/selection/PolygonFractionField.vue'
import NumericField from '@/components/selection/NumericField.vue'
import PolygonOrder from '@/components/specification/TruncationRule/order.vue'
import BackgroundFaciesSpecification from '@/components/specification/Facies/background.vue'
import type NonCubic from '@/utils/domain/truncationRule/nonCubic'
import type NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import type { HeaderItems } from '@/utils/typing'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { computed } from 'vue'
import type { MaybeFmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'

const props = defineProps<{ value: NonCubic }>()

const polygons = computed(() => props.value?.backgroundPolygons ?? [])
const hasMultipleFaciesSpecified = computed(() =>
  hasFaciesSpecifiedForMultiplePolygons(polygons.value),
)

const headers = computed<HeaderItems>(() => [
  {
    text: 'Angle',
    value: 'angle',
  },
  {
    text: 'Facies',
    value: 'facies',
  },
  ...(hasMultipleFaciesSpecified.value
    ? [
        {
          text: 'Probability Fraction',
          value: 'fraction',
          headerProps: {
            help: 'The fraction of the facies probability assigned to the individual polygon',
          },
        },
      ]
    : []),
  {
    text: 'Order',
    value: 'order',
  },
])

async function updateAngle(
  item: NonCubicPolygon,
  value: MaybeFmuUpdatable | null,
): Promise<void> {
  if (value !== null)
  item.angle = typeof value === "number" ? {
    value,
    updatable: false
  } : value
}

function isLast(polygon: NonCubicPolygon): boolean {
  return (
    polygons.value.findIndex(({ id }) => id === polygon.id) ===
    polygons.value.length - 1
  )
}
</script>

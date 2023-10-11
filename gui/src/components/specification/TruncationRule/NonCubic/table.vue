<template>
  <base-table
    :headers="headers"
    :items="polygons"
    :custom-sort="ordering"
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
            @input="(angle) => updateAngle(item, angle)"
          />
        </td>
        <td class="text-left">
          <background-facies-specification :value="item" :rule="value" />
        </td>
        <td v-if="hasMultipleFaciesSpecified">
          <polygon-fraction-field :value="item" :rule="value" />
        </td>
        <td>
          <polygon-order :value="item" :rule="value" min-polygons="2" />
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
import NonCubic from '@/utils/domain/truncationRule/nonCubic'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import { HeaderItems } from '@/utils/typing'
import { sortByOrder } from '@/utils'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { computed } from 'vue'
import { useStore } from '../../../../store'

const props = defineProps<{ value: NonCubic }>()
const store = useStore()

// TODO: Include 'help' messages
const polygons = computed(() => props.value?.backgroundPolygons ?? [])
const hasMultipleFaciesSpecified = computed(() =>
  hasFaciesSpecifiedForMultiplePolygons(polygons.value),
)

const headers: HeaderItems = [
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
          help: 'The fraction of the facies probability assigned to the individual polygon',
        },
      ]
    : []),
  {
    text: 'Order',
    value: 'order',
  },
]

function ordering(
  items: NonCubicPolygon[],
  index: number,
  isDescending: boolean,
): NonCubicPolygon[] {
  return sortByOrder(items, index, isDescending)
}

async function updateAngle(
  item: NonCubicPolygon,
  value: number,
): Promise<void> {
  await store.dispatch('truncationRules/changeAngles', {
    rule: props.value,
    polygon: item,
    value,
  })
}

function isLast(polygon: NonCubicPolygon): boolean {
  return (
    polygons.value.findIndex(({ id }) => id === polygon.id) ===
    polygons.value.length - 1
  )
}
</script>

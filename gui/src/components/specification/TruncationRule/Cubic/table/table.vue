<template>
  <base-table :headers="headers" :items="polygons" must-sort>
    <template #item="{ item }: { item: CubicPolygon }">
      <tr>
        <td v-for="index in value.levels" :key="index">
          {{
            item.atLevel === index ? item.level.slice(0, index).join('.') : ''
          }}
        </td>
        <td>
          <background-facies-specification :value="item" :rule="value" />
        </td>
        <td v-if="hasMultipleFaciesSpecified">
          <polygon-fraction-field :value="item" :rule="value" />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script setup lang="ts">
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import BackgroundFaciesSpecification from '@/components/specification/Facies/background.vue'
import PolygonFractionField from '@/components/selection/PolygonFractionField.vue'

import { CubicPolygon } from '@/utils/domain'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'

import Cubic from '@/utils/domain/truncationRule/cubic'
import { computed } from 'vue'

function makeLevelsHeader(levels: number): { text: string; value: string }[] {
  return [...new Array(levels)].map((_, index) => {
    return {
      text: `Level ${index + 1}`,
      value: 'level',
    }
  })
}

const props = defineProps<{ value: Cubic }>()

const polygons = computed<CubicPolygon[]>(() => props.value.backgroundPolygons)
const hasMultipleFaciesSpecified = computed(() =>
  hasFaciesSpecifiedForMultiplePolygons(polygons.value),
)

const headers = [
  ...makeLevelsHeader(props.value.levels),
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
]
</script>

<template>
  <base-table
    :headers="headers"
    :items="polygons"
    @input.stop
  >
    <template #item="{ item: polygon }">
      <tr>
        <td class="text-left">
          {{ polygon.name }}
        </td>
        <td class="text-left">
          <facies-specification
            :value="polygon"
            :rule="value"
            :disable="isFaciesUsed(polygon)"
            clearable
          />
        </td>
        <td>
          <fraction-field
            v-if="!!polygon.slantFactor"
            :model-value="polygon.slantFactor"
            fmu-updatable
            @update:model-value="(factor) => updateFactor(polygon, factor)"
          />
          <slot v-else />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script setup lang="ts">
import FractionField from '@/components/selection/FractionField.vue'
import FaciesSpecification from '@/components/specification/Facies/index.vue'
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import type { Bayfill, BayfillPolygon, Facies } from '@/utils/domain'
import { computed } from 'vue'
import type { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import { requireSlantFactor } from '@/utils/domain/polygon/bayfill'

const props = defineProps<{ value: Bayfill }>()

const polygons = computed(() => props.value?.backgroundPolygons ?? [])
const headers = [
  { text: 'Polygon', value: 'name' },
  { text: 'Facies', value: 'facies' },
  { text: 'Slant Factor', value: 'factor' },
]

function isFaciesUsed(polygon: BayfillPolygon): (facies: Facies) => boolean {
  const otherPolygons = props.value.backgroundPolygons.filter(
    ({ name }): boolean => name !== polygon.name,
  )
  return (facies: Facies): boolean =>
    otherPolygons.filter((polygon) => facies === polygon.facies).length > 0
}

function updateFactor(
  item: BayfillPolygon,
  value: number | FmuUpdatable | null,
): void {
  if (requireSlantFactor(item.name)) {
    if (typeof  value === 'number') {
      value = new FmuUpdatableValue(value)
    }
    item.slantFactor = value
  }
}
</script>

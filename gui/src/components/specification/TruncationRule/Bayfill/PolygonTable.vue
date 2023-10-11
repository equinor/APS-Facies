<template>
  <base-table
    :headers="headers"
    :items="polygons"
    @input.stop
  >
    <template #item="{ item: polygon }">
      <tr>
        <td class="text-left">
          <optional-help-item :value="polygon.name" />
        </td>
        <td class="text-left">
          <!--TODO: Figure out why input happens twice-->
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
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import FaciesSpecification from '@/components/specification/Facies/index.vue'
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import { Bayfill, BayfillPolygon, Facies } from '@/utils/domain'
import { computed } from 'vue'

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
  value: number,
): void {
  // TODO: [sindre] How do FmuUpdatable values work?
  // TODO: [seb] Make usages decide if they should use fmuUpdatable
  item.slantFactor = value
}
</script>

<template>
  <base-table
    :headers="headers"
    :items="items"
    no-data-text="No Facies selected"
    elevation="0"
  >
    <template #item="{ item: facies }">
      <tr>
        <td>{{ facies.alias }}</td>
        <td v-if="useProbabilityCubes">
          <v-autocomplete
            :value="facies.probabilityCube"
            :items="probabilityCubes"
            clearable
            @input="(cube: string) => changeProbabilityCube(facies, cube)"
          />
        </td>
        <td v-if="useProbabilityCubes">
          {{ parseFloat(facies.previewProbability).toFixed(2) }}
        </td>
        <td v-else>
          <fraction-field
            :model-value="facies.previewProbability"
            label=""
            dense
            @input="(probability) => changeProbability(facies, probability)"
          />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script setup lang="ts">
import FractionField from '@/components/selection/FractionField.vue'
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import Facies, { ProbabilityCube } from '@/utils/domain/facies/local'
import type { HeaderItem, ListItem } from '@/utils/typing'

import { hasCurrentParents } from '@/utils'
import { useStore } from '../../../store'
import { computed } from 'vue'

const store = useStore()
const facies = computed(() =>
  (Object.values(store.state.facies.available) as Facies[]).filter((facies) =>
    hasCurrentParents(facies, store.getters),
  ),
)

const probabilityCubes = computed<ListItem<ProbabilityCube>[]>(() =>
  [{ title: '', disabled: false }].concat(
    store.state.parameters.probabilityCube.available.map(
      (parameter: string) => {
        return {
          title: parameter,
          props: {
            disabled: facies.value
              .map((facies) => facies.probabilityCube)
              .includes(parameter),
          },
        }
      }
    ),
  ),
)

const useProbabilityCubes = computed(
  () => !store.getters['facies/constantProbability'](),
)

const items = computed(() => facies.value.sort((a, b) => a.code - b.code))

const headers = computed<HeaderItem[]>(() => {
  if (useProbabilityCubes.value) {
    return [
      { text: 'Facies', value: 'name' },
      { text: 'Probability Cube', value: 'probabilityCube' },
      { text: 'Preview Probability', value: 'previewProbability' },
    ]
  } else {
    return [
      { text: 'Facies', value: 'name' },
      { text: 'Probability', value: 'previewProbability' },
    ]
  }
})

function changeProbabilityCube(facies: Facies, probabilityCube: string): void {
  store.dispatch('facies/changeProbabilityCube', {
    facies,
    probabilityCube,
  })
}

function changeProbability(facies: Facies, previewProbability: number): void {
  store.dispatch('facies/changePreviewProbability', {
    facies,
    previewProbability,
  })
}
</script>

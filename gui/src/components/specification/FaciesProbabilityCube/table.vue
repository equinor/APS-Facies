<template>
  <base-table
    :headers="headers"
    :items="items"
    no-data-text="No Facies selected"
    elevation="0"
  >
    <template #item="{ item: facies }: { item: Facies }">
      <tr>
        <td>{{ facies.alias }}</td>
        <td v-if="useProbabilityCubes">
          <v-autocomplete
            :model-value="facies.probabilityCube"
            :items="probabilityCubes"
            clearable
            @update:model-value="(cube: ProbabilityCube) => changeProbabilityCube(facies, cube)"
          />
        </td>
        <td v-if="useProbabilityCubes">
          {{ facies.previewProbability !== null ? facies.previewProbability.toFixed(2) : '-' }}
        </td>
        <td v-else>
          <fraction-field
            :model-value="facies.previewProbability"
            @update:model-value="
              (probability) => changeProbability(facies, probability as PROBABILITY)
            "
            label=""
            dense
          />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script setup lang="ts">
import FractionField from '@/components/selection/FractionField.vue'
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import type { ProbabilityCube } from '@/utils/domain/facies/local'
import type Facies from '@/utils/domain/facies/local'
import type { HeaderItem, ListItem } from '@/utils/typing'

import { computed } from 'vue'
import { useFaciesStore } from '@/stores/facies'
import { useParameterProbabilityCubeStore } from '@/stores/parameters/probability-cube'
import { useRootStore } from '@/stores'
import type { PROBABILITY } from '@/utils/domain/types'

const rootStore = useRootStore()
const faciesStore = useFaciesStore()

const facies = computed(() => faciesStore.selected)

const probabilityCubes = computed<ListItem<ProbabilityCube>[]>(() =>
  [{ title: '', props: { disabled: false } }].concat(
    useParameterProbabilityCubeStore().available.map(parameter => {
      return {
        title: parameter,
        props: {
          disabled: facies.value
            .map((facies) => facies.probabilityCube)
            .includes(parameter),
        }
      }
    }),
  ),
)

const useProbabilityCubes = computed(
  () => !faciesStore.constantProbability(rootStore.parent),
)

const items = computed<Facies[]>(() => [...facies.value].sort((a, b) => a.code - b.code))

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

function changeProbabilityCube(facies: Facies, probabilityCube: ProbabilityCube): void {
  faciesStore.changeProbabilityCube(facies, probabilityCube)
}

function changeProbability(
  facies: Facies,
  previewProbability: PROBABILITY | null,
): void {
  faciesStore.changePreviewProbability(facies, previewProbability)
}
</script>

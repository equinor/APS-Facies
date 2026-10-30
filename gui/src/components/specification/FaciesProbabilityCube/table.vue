<template>
  <table class="probability-table w-100 text-body-2">
    <thead class="text-no-wrap">
      <tr>
        <th scope="col">Facies</th>
        <th v-if="useProbabilityCubes" scope="col">Probability cube</th>
        <th scope="col" class="probability-table__value">
          {{ probabilityHeading }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="facies in selectedFacies" :key="facies.id">
        <th scope="row" class="font-weight-regular">{{ facies.alias }}</th>
        <td v-if="useProbabilityCubes">
          <labeled-field
            :label="`Probability cube for ${facies.alias}`"
            hide-label
          >
            <template #default="{ fieldAttrs }">
              <v-autocomplete
                v-bind="fieldAttrs"
                :model-value="facies.probabilityCube"
                :items="probabilityCubes"
                :menu-props="{ maxWidth: 0 }"
                clearable
                @update:model-value="
                  (cube: ProbabilityCube | null) =>
                    faciesStore.changeProbabilityCube(facies, cube)
                "
              />
            </template>
          </labeled-field>
        </td>
        <td>
          <labeled-field
            :label="`${probabilityHeading} for ${facies.alias}`"
            hide-label
          >
            <template #default="{ fieldAttrs }">
              <v-text-field
                v-if="useProbabilityCubes"
                v-bind="fieldAttrs"
                :model-value="facies.previewProbability?.toFixed(3)"
                :disabled="facies.previewProbability === null"
                class="pointer-events-none"
                tabindex="-1"
                readonly
              />
              <fraction-field
                v-else
                v-bind="fieldAttrs"
                :model-value="facies.previewProbability"
                variant="outlined"
                @update:model-value="
                  (probability) =>
                    faciesStore.changePreviewProbability(
                      facies,
                      probability as PROBABILITY | null,
                    )
                "
              />
            </template>
          </labeled-field>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import FractionField from '@/components/selection/FractionField.vue'
import LabeledField from '@/components/baseComponents/LabeledField.vue'

import type { ProbabilityCube } from '@/utils/domain/facies/local'
import type { PROBABILITY } from '@/utils/domain/types'
import type { ListItem } from '@/utils/typing'

import { computed } from 'vue'
import { useFaciesStore } from '@/stores/facies'
import { useParameterProbabilityCubeStore } from '@/stores/parameters/probability-cube'
import { useRootStore } from '@/stores'

const rootStore = useRootStore()
const faciesStore = useFaciesStore()
const probabilityCubeStore = useParameterProbabilityCubeStore()

const selectedFacies = computed(() => faciesStore.selected)

const probabilityCubes = computed<ListItem<ProbabilityCube>[]>(() =>
  probabilityCubeStore.available.map((parameter) => ({
    title: parameter,
    props: {
      disabled: selectedFacies.value.some(
        (facies) => facies.probabilityCube === parameter,
      ),
    },
  })),
)

const useProbabilityCubes = computed(
  () => !faciesStore.constantProbability(rootStore.parent),
)

const probabilityHeading = computed(() =>
  useProbabilityCubes.value ? 'Preview probability' : 'Probability',
)
</script>

<style lang="scss" scoped>
.probability-table {
  table-layout: fixed;
  border-collapse: collapse;

  th,
  td {
    padding: 0.25rem 0;
    text-align: start;
  }

  tr > * + * {
    padding-left: 0.625rem;
  }

  td:last-child :deep(input) {
    text-align: end;
  }

  .probability-table__value {
    width: 9.5rem;
  }
}
</style>

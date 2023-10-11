<template>
  <v-row class="fill-height" align="center" justify="space-around">
    <v-col>
      <v-checkbox
        v-model="useProbabilityCubes"
        v-tooltip.bottom="
          'Toggles whether constant probabilities, or probability cubes should be used'
        "
        :disabled="disabled"
        label="Use cubes"
      />
    </v-col>
    <v-col>
      <wait-btn
        v-if="useProbabilityCubes"
        v-tooltip.bottom="'Calculate average probability (for previewer)'"
        :disabled="!canCalculateAverages"
        :waiting="calculatingAverages"
        color=""
        @click.stop="average"
      >
        Average
      </wait-btn>
      <v-btn
        v-else
        v-tooltip.bottom="'Normalize the probabilities'"
        :disabled="!shouldNormalize"
        @click.stop="normalize"
      >
        Normalize
      </v-btn>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import WaitBtn from '@/components/baseComponents/WaitButton.vue'

import { RootState } from '@/store/typing'
import { ProbabilityCube } from '@/utils/domain/facies/local'

import { hasCurrentParents, notEmpty } from '@/utils'
import { isCloseToUnity } from '@/utils/helpers/simple'
import { ref } from 'vue'
import { computed } from 'vue'
import { useStore } from '../../../store'

const store = useStore()
const calculatingAverages = ref(false)

const selectedFacies = computed(() => {
  const state: RootState = store.state
  const getters = store.getters
  return Object.values(state.facies.available).filter((facies) =>
    hasCurrentParents(facies, getters),
  )
})

const probabilityCubeParameters = computed<ProbabilityCube[]>(
  () =>
    selectedFacies.value
      .map((facies) => facies.probabilityCube)
      .filter((param) => notEmpty(param)) as ProbabilityCube[],
)

const useProbabilityCubes = computed({
  get: () => !store.getters['facies/constantProbability'](),
  set: (value: boolean) => store.dispatch('facies/toggleConstantProbability'),
})

const disabled = computed(() => selectedFacies.value.length === 0)

const canCalculateAverages = computed(
  () =>
    !disabled.value &&
    !calculatingAverages.value &&
    probabilityCubeParameters.value.length !== 0,
)

const shouldNormalize = computed(
  () => !disabled.value && !isCloseToUnity(store.getters['facies/cumulative']),
)

async function average() {
  calculatingAverages.value = true
  try {
    await store.dispatch('facies/averageProbabilityCubes', {
      probabilityCubes: probabilityCubeParameters.value,
    })
  } finally {
    calculatingAverages.value = false
  }
}

async function normalize() {
  const normalize = selectedFacies.value.every(
    (facies) => facies.previewProbability === null,
  )
    ? 'normalizeEmpty'
    : 'normalize'
  await store.dispatch(`facies/${normalize}`)
}
</script>

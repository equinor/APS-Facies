<template>
  <div class="d-flex align-center justify-space-between ga-3">
    <v-checkbox
      v-model="useProbabilityCubes"
      v-tooltip.bottom="
        'Toggles whether constant probabilities, or probability cubes should be used'
      "
      :disabled="disabled"
      label="Use cubes"
      density="compact"
      hide-details
      class="use-cubes"
    />
    <action-button
      v-if="useProbabilityCubes"
      v-tooltip.bottom="'Calculate average probability (for previewer)'"
      :disabled="!canCalculateAverages"
      :loading="calculatingAverages"
      @click.stop="average"
    >
      Average
    </action-button>
    <action-button
      v-else
      v-tooltip.bottom="'Normalize the probabilities'"
      :disabled="!shouldNormalize"
      @click.stop="normalize"
    >
      Normalize
    </action-button>
  </div>
</template>

<script setup lang="ts">
import ActionButton from '@/components/baseComponents/ActionButton.vue'

import type { ProbabilityCube } from '@/utils/domain/facies/local'

import { notEmpty } from '@/utils'
import { isCloseToUnity } from '@/utils/helpers/simple'
import { ref, computed } from 'vue'
import { useFaciesStore } from '@/stores/facies'
import { useRootStore } from '@/stores'

const calculatingAverages = ref(false)

const faciesStore = useFaciesStore()
const rootStore = useRootStore()
const selectedFacies = computed(() => faciesStore.selected)

const probabilityCubeParameters = computed<ProbabilityCube[]>(
  () =>
    selectedFacies.value
      .map((facies) => facies.probabilityCube)
      .filter((param) => notEmpty(param)) as ProbabilityCube[],
)

const useProbabilityCubes = computed({
  get: () => !faciesStore.constantProbability(rootStore.parent),
  set: (value: boolean) => {
    if (value !== !faciesStore.constantProbability(rootStore.parent)) {
      faciesStore.toggleConstantProbability()
    }
  },
})

const disabled = computed(() => selectedFacies.value.length === 0)

const canCalculateAverages = computed(
  () =>
    !disabled.value &&
    !calculatingAverages.value &&
    probabilityCubeParameters.value.length !== 0,
)

const shouldNormalize = computed(
  () => !disabled.value && !isCloseToUnity(faciesStore.cumulative),
)

async function average() {
  calculatingAverages.value = true
  try {
    await faciesStore.averageProbabilityCubes({
      probabilityCubes: probabilityCubeParameters.value,
    })
  } finally {
    calculatingAverages.value = false
  }
}

function normalize() {
  const allEmpty = selectedFacies.value.every(
    (facies) => facies.previewProbability === null,
  )

  if (allEmpty) {
    faciesStore.normalizeEmpty()
  } else {
    faciesStore.normalize()
  }
}
</script>

<style lang="scss" scoped>
.use-cubes :deep(.v-label) {
  padding-left: 0.5rem;
}
</style>

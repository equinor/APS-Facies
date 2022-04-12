<template>
  <v-row
    class="fill-height"
    align="center"
    justify="space-around"
  >
    <v-col>
      <v-checkbox
        v-model="useProbabilityCubes"
        v-tooltip.bottom="'Toggles whether constant probabilities, or probability cubes should be used'"
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

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import WaitBtn from '@/components/baseComponents/WaitButton.vue'

import { RootState } from '@/store/typing'
import { ProbabilityCube } from '@/utils/domain/facies/local'

import { hasCurrentParents, notEmpty } from '@/utils'
import { Facies } from '@/utils/domain'
import { isCloseToUnity } from '@/utils/helpers/simple'

@Component({
  components: {
    WaitBtn,
  },
})
export default class FaciesProbabilityCubeHeader extends Vue {
  calculatingAverages = false

  get probabilityCubeParameters (): ProbabilityCube[] {
    return (this.selectedFacies.map(facies => facies.probabilityCube)
      .filter(param => notEmpty(param)) as ProbabilityCube[])
  }

  get selectedFacies (): Facies[] {
    const state: RootState = this.$store.state
    const getters = this.$store.getters
    return Object.values(state.facies.available).filter(facies => hasCurrentParents(facies, getters))
  }

  get useProbabilityCubes (): boolean { return !this.$store.getters['facies/constantProbability']() }
  set useProbabilityCubes (value) { this.$store.dispatch('facies/toggleConstantProbability') }

  get canCalculateAverages (): boolean { return !this.disabled && !this.calculatingAverages && this.probabilityCubeParameters.length !== 0 }

  get disabled (): boolean { return this.selectedFacies.length === 0 }

  get shouldNormalize (): boolean { return !this.disabled && !isCloseToUnity(this.$store.getters['facies/cumulative']) }

  async average (): Promise<void> {
    this.calculatingAverages = true
    try {
      await this.$store.dispatch('facies/averageProbabilityCubes', { probabilityCubes: this.probabilityCubeParameters })
    } finally {
      this.calculatingAverages = false
    }
  }

  async normalize (): Promise<void> {
    const normalize = this.selectedFacies
      .every(facies => facies.previewProbability === null)
      ? 'normalizeEmpty'
      : 'normalize'
    await this.$store.dispatch(`facies/${normalize}`)
  }
}
</script>

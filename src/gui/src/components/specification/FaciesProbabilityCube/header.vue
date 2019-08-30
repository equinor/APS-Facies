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

import { RootState, Store } from '@/store/typing'

import { hasCurrentParents, notEmpty } from '@/utils'
import { Facies } from '@/utils/domain'
import { isCloseToUnity } from '@/utils/helpers/simple'

@Component({
  components: {
    WaitBtn,
  },
})
export default class FaciesProbabilityCubeHeader extends Vue {
  calculatingAverages: boolean = false

  get probabilityCubeParameters () {
    const state = (this.$store as Store).state
    return Object.values(state.facies.available)
      .map(facies => facies.probabilityCube)
      .filter(param => notEmpty(param))
  }

  get selectedFacies (): Facies[] {
    const state: RootState = this.$store.state
    const getters = this.$store.getters
    return Object.values(state.facies.available).filter(facies => hasCurrentParents(facies, getters))
  }

  get useProbabilityCubes () { return !this.$store.getters['facies/constantProbability']() }
  set useProbabilityCubes (value) { this.$store.dispatch('facies/toggleConstantProbability') }

  get canCalculateAverages () { return !this.disabled && !this.calculatingAverages && this.probabilityCubeParameters.length !== 0 }

  get disabled () { return this.selectedFacies.length === 0 }

  get shouldNormalize () { return !this.disabled && !isCloseToUnity(this.$store.getters['facies/cumulative']) }

  validate () {}

  async average () {
    this.calculatingAverages = true
    try {
      await this.$store.dispatch('facies/averageProbabilityCubes', { probabilityCubes: this.probabilityCubeParameters })
    } finally {
      this.calculatingAverages = false
    }
  }

  async normalize () {
    const normalize = this.selectedFacies
      .every(facies => facies.previewProbability === null)
      ? 'normalizeEmpty'
      : 'normalize'
    await this.$store.dispatch(`facies/${normalize}`)
  }
}
</script>

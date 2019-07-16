<template>
  <v-layout
    align-center
    justify-start
    row
    fill-height
    wrap
  >
    <v-flex>
      <v-tooltip bottom>
        <v-checkbox
          slot="activator"
          v-model="useProbabilityCubes"
          :disabled="disabled"
          label="Use cubes"
        />
        <span>Toggles whether constant probabilities, or probability cubes should be used</span>
      </v-tooltip>
    </v-flex>
    <v-flex>
      <v-tooltip
        v-show="useProbabilityCubes"
        bottom
      >
        <wait-btn
          slot="activator"
          :disabled="!canCalculateAverages"
          :waiting="calculatingAverages"
          color=""
          @click.stop="average"
        >
          Average
        </wait-btn>
        <span>Calculate average probability (for previewer)</span>
      </v-tooltip>
      <v-tooltip
        v-show="!useProbabilityCubes"
        bottom
      >
        <v-btn
          slot="activator"
          :disabled="!shouldNormalize"
          @click.stop="normalize"
        >
          Normalize
        </v-btn>
        <span>Normalize the probabilities</span>
      </v-tooltip>
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import { Store } from '@/store/typing'
import { Component, Vue } from 'vue-property-decorator'

import { hasCurrentParents, notEmpty } from '@/utils'

import WaitBtn from '@/components/baseComponents/WaitButton.vue'

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
  get zoneCodes () {
    return Object.values((this.$store as Store).state.zones.available)
      .filter(zone => !!zone.selected)
      .map(zone => zone.code)
  }
  get selectedFacies () {
    const state = this.$store.state
    const getters = this.$store.getters
    return Object.values(state.facies.available).filter(facies => hasCurrentParents(facies, getters))
  }

  get useProbabilityCubes () { return !this.$store.getters['facies/constantProbability']() }
  set useProbabilityCubes (value) { this.$store.dispatch('facies/toggleConstantProbability') }

  get canCalculateAverages () { return !this.disabled && !this.calculatingAverages && this.probabilityCubeParameters.length !== 0 }

  get disabled () { return this.selectedFacies.length === 0 }

  get shouldNormalize () { return !this.disabled && this.$store.getters['facies/cumulative'] !== 1 }

  validate () {}

  async average () {
    this.calculatingAverages = true
    try {
      await this.$store.dispatch('facies/averageProbabilityCubes', { probabilityCubes: this.probabilityCubeParameters })
    } finally {
      this.calculatingAverages = false
    }
  }

  normalize () {
    return this.$store.dispatch('facies/normalize')
  }
}
</script>

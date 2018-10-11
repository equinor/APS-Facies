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
    <v-flex
    >
      <v-tooltip
        v-show="useProbabilityCubes"
        bottom
      >
        <v-btn
          slot="activator"
          :disabled="!canCalculateAverages"
          @click.stop="average"
        >Average</v-btn>
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
        >Normalize</v-btn>
        <span>Normalize the probabilities</span>
      </v-tooltip>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapState } from 'vuex'

import rms from '@/api/rms'
import { notEmpty } from '@/utils'

export default {
  data () {
    return {
      calculatingAverages: false,
    }
  },

  computed: {
    ...mapState({
      selectedFacies: state => Object.values(state.facies.available).filter(facies => facies.selected),
      probabilityCubeParameters: state => Object.values(state.facies.available)
        .map(facies => facies.probabilityCube)
        .filter(param => notEmpty(param)),
      zoneCodes: state => Object.values(state.zones.available)
        .filter(zone => !!zone.selected)
        .map(zone => zone.code)
    }),
    useProbabilityCubes: {
      get () { return !this.$store.state.facies.constantProbability },
      set (value) { this.$store.dispatch('facies/toggleConstantProbability') },
    },
    canCalculateAverages () { return !this.disabled && !this.calculatingAverages && this.probabilityCubeParameters.length !== 0 },
    disabled () { return this.selectedFacies.length === 0 },
    shouldNormalize () { return !this.disabled && this.$store.getters['facies/cumulative'] !== 1 }
  },

  methods: {
    validate () {},
    average () {
      this.calculatingAverages = true
      rms.averageProbabilityCubes(this.$store.getters.gridModel, this.probabilityCubeParameters, this.zoneCodes)
        .then(probabilityCubes => {
          // Result in the form of { probCubeName_1: average, ...}
          this.$store.dispatch('facies/updateProbabilities', { probabilityCubes })
            .then(() => { this.calculatingAverages = false })
        })
    },
    normalize () {
      this.$store.dispatch('facies/normalize')
    }
  },
}
</script>

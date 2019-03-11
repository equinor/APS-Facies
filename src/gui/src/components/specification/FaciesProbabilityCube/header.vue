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
        <v-btn
          slot="activator"
          :disabled="!canCalculateAverages"
          @click.stop="average"
        >
          Average
        </v-btn>
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

<script>
import { mapState } from 'vuex'

import rms from '@/api/rms'
import { hasCurrentParents, notEmpty } from '@/utils'

export default {
  data () {
    return {
      calculatingAverages: false,
    }
  },

  computed: {
    ...mapState({
      probabilityCubeParameters: state => Object.values(state.facies.available)
        .map(facies => facies.probabilityCube)
        .filter(param => notEmpty(param)),
      zoneCodes: state => Object.values(state.zones.available)
        .filter(zone => !!zone.selected)
        .map(zone => zone.code)
    }),
    selectedFacies () {
      const state = this.$store.state
      const getters = this.$store.getters
      return Object.values(state.facies.available).filter(facies => hasCurrentParents(facies, getters))
    },
    useProbabilityCubes: {
      get () { return !this.$store.getters['facies/constantProbability']() },
      set (value) { this.$store.dispatch('facies/toggleConstantProbability') },
    },
    canCalculateAverages () { return !this.disabled && !this.calculatingAverages && this.probabilityCubeParameters.length !== 0 },
    disabled () { return this.selectedFacies.length === 0 },
    shouldNormalize () { return !this.disabled && this.$store.getters['facies/cumulative'] !== 1 }
  },

  methods: {
    validate () {},
    async average () {
      this.calculatingAverages = true
      const gridModel = this.$store.getters.gridModel
      const zoneNumber = this.$store.getters.zone.code
      let regionParameter = null
      let regionNumber = null
      if (this.$store.getters.useRegions) {
        regionParameter = this.$store.getters.regionParameter
        const region = this.$store.state.getters.region
        if (region) regionNumber = region.code
      }
      try {
        const probabilityCubes = await rms.averageProbabilityCubes(gridModel, this.probabilityCubeParameters, zoneNumber, regionParameter, regionNumber)
        // Result in the form of { probCubeName_1: average, ...}
        await this.$store.dispatch('facies/updateProbabilities', { probabilityCubes })
        await this.normalize()
      } finally {
        this.calculatingAverages = false
      }
    },
    normalize () {
      return this.$store.dispatch('facies/normalize')
    }
  },
}
</script>

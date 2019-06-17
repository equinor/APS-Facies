<template>
  <v-container
    align-start
    justify-start
  >
    <v-expansion-panel
      v-model="expanded"
    >
      <v-expansion-panel-content>
        <div slot="header">
          Preview
        </div>
        <preview-header
          :value="rule"
        />
        <v-card>
          <v-layout
            v-if="!!rule"
            row
            wrap
          >
            <v-flex xs1 />
            <v-flex>
              <h3>Truncation rule</h3>
              <truncation-map
                :value="rule"
              />
            </v-flex>
            <v-flex xs1 />
            <v-flex>
              <h3>Realization</h3>
              <facies-realization
                :value="rule"
              />
            </v-flex>
            <v-flex xs1 />
            <v-flex xs12>
              <gaussian-plots
                v-if="isGaussianFieldsSimulated"
                :value="fields"
              />
            </v-flex>
          </v-layout>
          <v-layout>
            <v-flex xs12>
              <cross-plots
                :value="fields"
              />
            </v-flex>
          </v-layout>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-container>
</template>

<script>
import TruncationMap from '@/components/plot/TruncationMap'
import FaciesRealization from '@/components/plot/FaciesRealization'
import GaussianPlots from '@/components/plot/GaussianPlot/multiple'

import PreviewHeader from '@/components/visualization/preview/header'
import CrossPlots from '@/components/plot/CrossPlot/multiple'

export default {
  components: {
    CrossPlots,
    PreviewHeader,
    GaussianPlots,
    FaciesRealization,
    TruncationMap,
  },

  data () {
    return {
      panels: null,
    }
  },

  computed: {
    expanded: {
      get () { return this.isGaussianFieldsSimulated ? 0 : null },
      set (val) { this.panels = val }
    },
    fields () { return Object.values(this.$store.getters.fields) },
    rule () { return this.$store.getters.truncationRule },
    isGaussianFieldsSimulated () {
      return this.fields.every(field => field.simulated)
    },
  },
}
</script>

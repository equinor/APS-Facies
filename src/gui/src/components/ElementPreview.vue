<template>
  <v-container
    align-start
    justify-start
  >
    <v-expansion-panel
      v-model="expanded"
    >
      <v-expansion-panel-content>
        <div slot="header">Preview</div>
        <preview-header/>
        <v-card>
          <v-layout
            row
            wrap
          >
            <v-flex xs6>
              <h3>Truncation rule</h3>
              <truncation-map
                :truncation-rule-id="ruleId"
              />
            </v-flex>
            <v-flex xs6>
              <h3>Realization</h3>
              <facies-realization
              />
            </v-flex>
            <v-flex xs12>
              <h3>Gaussian Random Fields</h3>
            </v-flex>
            <gaussian-plots
              v-if="isGaussianFieldsSimulated"
              :value="fields"
            />
            <v-flex xs12>
              <h3>Cross plots</h3>
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

export default {
  components: {
    PreviewHeader,
    GaussianPlots,
    FaciesRealization,
    TruncationMap,
  },

  data () {
    return {
      panels: null,
      faciesRealization: [],
    }
  },

  computed: {
    expanded: {
      get () { return [!!this.isGaussianFieldsSimulated] },
      set (val) { this.panels = val }
    },
    fields () { return Object.values(this.$store.getters.fields) },
    rule () { return this.$store.getters.truncationRule },
    ruleId () { return this.rule ? this.rule.id : '' },
    isGaussianFieldsSimulated () {
      return this.fields.every(field => field._data.length > 0 && field._data[0].length > 0)
    },
  },
}
</script>

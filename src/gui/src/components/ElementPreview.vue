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

<script lang="ts">
import { Store } from '@/store/typing'
import { Component, Vue } from 'vue-property-decorator'

import { Optional } from '@/utils/typing'

import TruncationMap from '@/components/plot/TruncationMap.vue'
import FaciesRealization from '@/components/plot/FaciesRealization.vue'
import GaussianPlots from '@/components/plot/GaussianPlot/multiple.vue'

import PreviewHeader from '@/components/visualization/preview/header.vue'
import CrossPlots from '@/components/plot/CrossPlot/multiple.vue'

@Component({
  components: {
    CrossPlots,
    PreviewHeader,
    GaussianPlots,
    FaciesRealization,
    TruncationMap,
  },
})
export default class ElementPreview extends Vue {
  panels: Optional<number> = null

  get expanded () { return this.isGaussianFieldsSimulated ? 0 : null }

  set expanded (val) { this.panels = val }

  get fields () { return Object.values((this.$store as Store).getters['fields']) }

  get rule () { return this.$store.getters.truncationRule }

  get isGaussianFieldsSimulated () {
    return this.fields.every(field => field.simulated)
  }
}
</script>

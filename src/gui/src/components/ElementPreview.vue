<template>
  <v-container
    align-start
    justify-start
  >
    <v-layout
      align-center
      justify-start
    >
      <section-title>Preview</section-title>
      <preview-header
        :value="rule"
      />
    </v-layout>
    <v-expansion-panels
      v-model="expanded"
      accordion
      multiple
    >
      <v-expansion-panel
        v-tooltip.bottom="truncationRuleError"
        :disabled="!hasTruncationRule"
      >
        <v-expansion-panel-header>
          <h3>Truncation rule</h3>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-flex
            justify-center
            align-center
          >
            <truncation-map
              v-if="!!rule"
              :value="rule"
            />
          </v-flex>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel
        v-tooltip.bottom="realizationError"
        :disabled="!hasRealization"
      >
        <v-expansion-panel-header>
          <h3>Realization</h3>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <facies-realization
            v-if="rule"
            :value="rule"
          />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>
          <h3>Gaussian Random Fields</h3>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <gaussian-plots
            :value="fields"
          />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>
          <h3>Cross plots</h3>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <cross-plots
            :value="fields"
          />
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'

import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'

import TruncationMap from '@/components/plot/TruncationMap.vue'
import FaciesRealization from '@/components/plot/FaciesRealization.vue'
import GaussianPlots from '@/components/plot/GaussianPlot/multiple.vue'

import PreviewHeader from '@/components/visualization/preview/header.vue'
import CrossPlots from '@/components/plot/CrossPlot/multiple.vue'

import { Store } from '@/store/typing'
import { GaussianRandomField, TruncationRule } from '@/utils/domain'

const TRUNCATION_MAP_ORDER = 0
const REALIZATION_ORDER = 1

@Component({
  components: {
    SectionTitle,
    CrossPlots,
    PreviewHeader,
    GaussianPlots,
    FaciesRealization,
    TruncationMap,
  },
})
export default class ElementPreview extends Vue {
  expanded: number[] = []

  get fields (): GaussianRandomField[] { return Object.values((this.$store as Store).getters['fields']) }

  get rule (): TruncationRule { return this.$store.getters.truncationRule }

  get hasTruncationRule (): boolean { return !!this.rule }

  get hasRealization (): boolean { return !!(this.rule && this.rule.realization) }

  get truncationRuleError (): string | undefined {
    return !this.hasTruncationRule
      ? 'No truncation rule has been specified'
      : undefined
  }
  get realizationError (): string | undefined {
    return this.truncationRuleError || !this.hasRealization
      ? 'The realization has not been simulated'
      : undefined
  }

  @Watch('rule')
  showTruncationMap (value: TruncationRule) {
    if (value) {
      if (this.isGaussianFieldsSimulated && !this.expanded.includes(TRUNCATION_MAP_ORDER)) {
        this.expanded.push(TRUNCATION_MAP_ORDER)
      }

      if (value.realization && !this.expanded.includes(REALIZATION_ORDER)) {
        this.expanded.push(REALIZATION_ORDER)
      }
    }
  }
}
</script>

<template>
  <v-container
    class="align justify"
    fluid
  >
    <v-row
      align="center"
      justify="center"
    >
      <section-title>Preview</section-title>
      <preview-header
        :value="rule"
      />
    </v-row>
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
          <v-col
            class="justify-center align-center"
          >
            <truncation-map
              v-if="!!rule"
              :value="rule"
            />
          </v-col>
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
          <h3>Transformed Gaussian Random Fields</h3>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <gaussian-plots
            :value="fields"
          />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel
        v-tooltip.bottom="crossPlotErrors"
        :disabled="!hasEnoughFieldsForCrossPlot"
      >
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
  get expanded (): number[] { return this.$store.getters['panels/preview'] }
  set expanded (indices) { this.$store.dispatch('panels/change', { type: 'preview', indices }) }

  get fields (): GaussianRandomField[] { return Object.values((this.$store as Store).getters.fields) }

  get rule (): TruncationRule { return this.$store.getters.truncationRule }

  get hasTruncationRule (): boolean { return !!this.rule }

  get hasRealization (): boolean { return !!(this.rule && this.rule.realization) }

  get hasEnoughFieldsForCrossPlot () { return this.fields.length >= 2 }

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

  get crossPlotErrors (): string | undefined {
    return !this.hasEnoughFieldsForCrossPlot
      ? 'There must be at least two Gaussian Fields before their cross variance plot can be made'
      : undefined
  }

  @Watch('fields', { deep: true })
  async showCrossPlot (fields: GaussianRandomField[]) {
    if (fields.length < 2) {
      await this.$store.dispatch('panels/close', { type: 'preview', panel: 'crossPlots' })
    }
  }

  @Watch('rule', { deep: true })
  async showTruncationMap (value: TruncationRule) {
    const type = 'preview'
    if (value) {
      await this.$store.dispatch('panels/open', { type, panel: 'truncationRuleMap' })

      await this.$store.dispatch(`panels/${value.realization ? 'open' : 'close'}`, { type, panel: 'truncationRuleRealization' })
    } else {
      await this.$store.dispatch('panels/close', { type, panel: ['truncationRuleMap', 'truncationRuleRealization'] })
    }
  }
}
</script>

<template>
  <v-container>
    <v-layout
      child-flex
      row
      wrap
    >
      <v-flex xs6>
        <gaussian-plot
          :value="value"
          expand
        />
      </v-flex>
      <v-flex xs1 />
      <v-flex xs5>
        <span>Variogram selection</span>
        <item-selection
          v-model="variogramType"
          :items="availableVariograms"
          :constraints="{ required: true }"
          label="Variogram"
        />
        <v-select
          v-model="alphaChannel"
          :items="alphaChannels"
          no-data-text="No truncation rule has been selected"
          label="Truncation Rule Role"
        >
          <template
            slot="item"
            slot-scope="{ item }"
          >
            ɑ<sub>{{ item }}</sub>
          </template>
          <template
            slot="selection"
            slot-scope="{ item }"
          >
            ɑ<sub>{{ item }}</sub>
          </template>
        </v-select>
        <icon-button
          :disabled="!canSimulate"
          icon="random"
          @click="() => updateSimulation(true)"
        />
        <icon-button
          :disabled="!canSimulate"
          :waiting="waitingForSimulation"
          icon="refresh"
          @click="() => updateSimulation(false)"
        />
        <icon-button
          icon="settings"
          @click="openVisualizationSettings"
        />
        <visualization-settings-dialog
          ref="visualisationSettings"
        />
      </v-flex>
      <!--New line-->
      <v-flex xs6>
        <span>Anisotropy direction</span>
        <anisotropy-direction
          :value="value"
        />
        <power-specification
          v-if="isGeneralExponential"
          :value="value"
        />
      </v-flex>
      <v-flex xs1 />
      <v-flex xs5>
        Ranges
        <range-specification
          :value="value"
        />
      </v-flex>
      <!--New line-->
      <trend-specification
        :value="value"
      />
    </v-layout>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import cloneDeep from 'lodash/cloneDeep'

import rms from '@/api/rms'

import { getId, hasValidChildren, invalidateChildren, notEmpty } from '@/utils'

import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'
import GaussianPlot from '@/components/plot/GaussianPlot/index.vue'
import TrendSpecification from '@/components/specification/Trend/index.vue'
import RangeSpecification from '@/components/specification/GaussianRandomField/Range.vue'
import AnisotropyDirection from '@/components/specification/GaussianRandomField/AnisotropyDirection.vue'
import PowerSpecification from '@/components/specification/GaussianRandomField/Power.vue'
import VisualizationSettingsDialog from '@/components/specification/GaussianRandomField/VisualizationSettingsDialog.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { TruncationRule } from '@/utils/domain'
import Field, { Trend, Variogram } from '@/utils/domain/gaussianRandomField'

@Component({
  components: {
    ItemSelection,
    IconButton,
    PowerSpecification,
    AnisotropyDirection,
    RangeSpecification,
    GaussianPlot,
    TrendSpecification,
    VisualizationSettingsDialog,
  },
})
export default class GaussianRandomField extends Vue {
  @Prop({ required: true })
  readonly value!: Field

  waitingForSimulation: boolean = false

  get rule (): TruncationRule { return this.$store.getters['truncationRule'] }

  get availableVariograms (): string[] { return this.$store.state.constants.options.variograms.available }

  get alphaChannel () {
    if (this.rule) {
      /* Channel is 1-indeed */
      const channel = 1 + this.rule.fields.findIndex(field => getId(field) === this.grfId)
      return channel || null
    } else {
      return null
    }
  }
  set alphaChannel (channel) { this.$store.dispatch('truncationRules/updateFields', { channel, selected: this.grfId }) }

  get alphaChannels () {
    return this.rule
      ? this.rule.fields.map((_, index: number) => index + 1)
      : []
  }

  get isGeneralExponential (): boolean { return this.variogramType === 'GENERAL_EXPONENTIAL' }

  get grfId () { return this.value.id }

  get variogram (): Variogram { return this.value.variogram }

  get trend (): Trend { return this.value.trend }

  get fieldName (): string { return this.value.name }

  get canSimulate (): boolean {
    return (
      notEmpty(this.variogramType)
      && (this.trend.use ? ['NONE'].indexOf(this.trend.type) === -1 : true)
      && this.isValid
      && !this.waitingForSimulation
    )
  }
  get isValid (): boolean { return hasValidChildren(this) }

  get variogramType () { return this.variogram.type }
  set variogramType (value) { this.$store.dispatch('gaussianRandomFields/variogramType', { field: this.value, value }) }

  beforeMount () {
    this.updateSimulation()
  }

  async simulation (renew: boolean = false): Promise<void> {
    if (renew) {
      await this.$store.dispatch('gaussianRandomFields/newSeed', { field: this.value })
    }
    await this.$store.dispatch('gaussianRandomFields/updateSimulationData', {
      field: this.value,
      data: await rms.simulateGaussianField({
        name: this.value.name,
        variogram: this.variogram,
        trend: this.trend,
        settings: this.$store.getters.simulationSettings(this.value),
      })
    })
  }

  async updateSimulation (renew: boolean = false): Promise<void> {
    this.waitingForSimulation = true
    try {
      await this.simulation(renew)
    } catch (reason) {
      invalidateChildren(this)
    } finally {
      this.waitingForSimulation = false
    }
  }

  async openVisualizationSettings (): Promise<void> {
    // @ts-ignore
    const { save, settings } = await (this.$refs.visualisationSettings as VisualizationSettingsDialog).open(cloneDeep(this.value.settings))
    if (save) {
      await this.$store.dispatch('gaussianRandomFields/changeSettings', {
        field: this.value,
        settings
      })
      await this.updateSimulation()
    }
  }
}
</script>

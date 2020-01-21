<template>
  <v-row
    no-gutters
  >
    <v-col cols="6">
      <gaussian-plot
        :value="value"
        expand
      />
    </v-col>
    <v-col cols="1" />
    <v-col cols="5">
      <span>Variogram selection</span>
      <item-selection
        v-model="variogramType"
        :items="availableVariograms"
        :constraints="{ required: true }"
        label="Variogram"
      />
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
    </v-col>
    <!--New line-->
    <v-col
      class="column"
      align-self="start"
      cols="6"
    >
      <span>Anisotropy direction</span>
      <anisotropy-direction
        :value="value"
        @update:error="e => update('anisotropyDirection', e)"
      />
      <power-specification
        v-if="isGeneralExponential"
        :value="value"
        @update:error="e => update('power', e)"
      />
    </v-col>
    <v-col cols="1" />
    <v-col cols="5">
      Ranges
      <range-specification
        :value="value"
        @update:error="e => update('range', e)"
      />
    </v-col>
    <!--New line-->
    <v-row>
      <trend-specification
        :value="value"
        @update:error="e => update('trend', e)"
      />
    </v-row>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import cloneDeep from 'lodash/cloneDeep'

import rms from '@/api/rms'
import { TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION } from '@/config'

import { invalidateChildren, notEmpty } from '@/utils'

import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'
import GaussianPlot from '@/components/plot/GaussianPlot/index.vue'
import TrendSpecification from '@/components/specification/Trend/index.vue'
import RangeSpecification from '@/components/specification/GaussianRandomField/Range.vue'
import AnisotropyDirection from '@/components/specification/GaussianRandomField/AnisotropyDirection.vue'
import PowerSpecification from '@/components/specification/GaussianRandomField/Power.vue'
import VisualizationSettingsDialog from '@/components/specification/GaussianRandomField/VisualizationSettingsDialog.vue'
import IconButton from '@/components/selection/IconButton.vue'

import Field, { Trend, Variogram } from '@/utils/domain/gaussianRandomField'

interface Invalid {
  anisotropyDirection: boolean
  power: boolean
  range: boolean
  trend: boolean
}

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

  waitingForSimulation = false
  invalid: Invalid = {
    anisotropyDirection: false,
    power: false,
    range: false,
    trend: false,
  }

  get availableVariograms (): string[] { return this.$store.state.constants.options.variograms.available }

  get isGeneralExponential (): boolean { return this.variogramType === 'GENERAL_EXPONENTIAL' }

  get variogram (): Variogram { return this.value.variogram }

  get trend (): Trend { return this.value.trend }

  get fieldName (): string { return this.value.name }

  get canSimulate (): boolean {
    return (
      notEmpty(this.variogramType)
      && (this.trend.use ? TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION.indexOf(this.trend.type) === -1 : true)
      && this.isValid
      && !this.waitingForSimulation
    )
  }

  get isValid (): boolean {
    return Object.values(this.invalid).every(invalid => !invalid)
  }

  get variogramType (): string { return this.variogram.type }
  set variogramType (value) { this.$store.dispatch('gaussianRandomFields/variogramType', { field: this.value, value }) }

  beforeMount (): void {
    if (!this.value.isRepresentative) {
      this.updateSimulation()
    }
  }

  async simulation (renew = false): Promise<void> {
    if (renew) {
      await this.$store.dispatch('gaussianRandomFields/newSeed', { field: this.value })
    }
    await this.$store.dispatch('gaussianRandomFields/updateSimulationData', {
      field: this.value,
      data: await rms.simulateGaussianField({
        name: this.value.name,
        variogram: this.variogram,
        trend: this.trend,
        settings: this.$store.getters.simulationSettings({ field: this.value }),
      })
    })
  }

  async updateSimulation (renew = false): Promise<void> {
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
    // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
    // @ts-ignore
    // eslint-disable-next-line security/detect-non-literal-fs-filename
    const { save, settings } = await (this.$refs.visualisationSettings as VisualizationSettingsDialog).open(cloneDeep(this.value.settings))
    if (save) {
      await this.$store.dispatch('gaussianRandomFields/changeSettings', {
        field: this.value,
        settings
      })
      await this.updateSimulation()
    }
  }

  update (type: string, value: boolean): void {
    Vue.set(this.invalid, type, value)
  }

  @Watch('isValid')
  async changeValidity (value: boolean): Promise<void> {
    await this.$store.dispatch('gaussianRandomFields/changeValidity', { field: this.value, value })
  }
}
</script>

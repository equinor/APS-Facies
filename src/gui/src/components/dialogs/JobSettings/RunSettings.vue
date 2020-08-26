<template>
  <settings-panel
    title="Run settings"
  >
    <v-row>
      <v-col cols="6">
        <numeric-field
          v-model="_maxAllowedFractionOfValuesOutsideTolerance"
          v-tooltip="'Max allowed fraction of grid cell values in probability cubes without proper normalization. <br> Default value is 10%'"
          label="Max allowed fraction of non-normalized grid cells"
          :ranges="{ min: 0, max: 100 }"
          unit="%"
        />
      </v-col>
      <v-col cols="6">
        <numeric-field
          v-model="_toleranceOfProbabilityNormalisation"
          v-tooltip="'If the sum of facies probabilities is outside the interval <br>[1-tolerance, 1+tolerance], an error message will be given (job will not run), <br>but if inside this interval, the probabilities will be normalized to 1.<br>Default value is 0.2.'"
          label="Max allowed tolerance for non-normalized probabilities"
          :ranges="{min: 0, max: 100 }"
          unit="%"
        />
      </v-col>
    </v-row>
  </settings-panel>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import NumericField from '../../selection/NumericField.vue'

import SettingsPanel from './SettingsPanel.vue'

@Component({
  components: {
    NumericField,
    SettingsPanel,
  },
})
export default class RunSettings extends Vue {
  @Prop({ required: true })
  readonly maxAllowedFractionOfValuesOutsideTolerance: number

  @Prop({ required: true })
  readonly toleranceOfProbabilityNormalisation: number

  get _maxAllowedFractionOfValuesOutsideTolerance (): number { return this.maxAllowedFractionOfValuesOutsideTolerance * 100 }
  set _maxAllowedFractionOfValuesOutsideTolerance (value: number) { this.$emit('update:maxAllowedFractionOfValuesOutsideTolerance', value / 100) }

  get _toleranceOfProbabilityNormalisation (): number { return this.toleranceOfProbabilityNormalisation * 100 }
  set _toleranceOfProbabilityNormalisation (value: number) { this.$emit('update:toleranceOfProbabilityNormalisation', value / 100) }
}
</script>

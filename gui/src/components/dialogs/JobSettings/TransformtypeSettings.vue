<template>
  <settings-panel
    title="Gaussian field transformation settings"
  >
    <v-select
      v-model="_transformType"
      v-tooltip="'Choose which transformation to use for GRF. <br> The empiric transformation will always be used when the GRF has a trend. <br> The Cumulative normal is recommended for GRF without trend when running ERT using localization.'"
      label="Transformation type"
      :items="transformTypes"
    />
  </settings-panel>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import SettingsPanel from './SettingsPanel.vue'

interface TransformType {
  value: number
  text: string
}

@Component({
  components: {
    SettingsPanel,
  },
})
export default class TransformtypeSettings extends Vue {
  @Prop({ required: true })
  readonly transformType: number

  get transformTypes (): TransformType[] {
    return [
      { value: 0, text: 'Empiric Distribution function from realization of GRF' },
      { value: 1, text: 'Cumulative Normal Distribution function' },
    ]
  }

  get _transformType (): number { return this.transformType }
  set _transformType (level: number) { this.$emit('update:transformType', level) }
}

</script>

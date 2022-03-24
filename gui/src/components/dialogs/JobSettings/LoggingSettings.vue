<template>
  <settings-panel title="Logging settings">
    <v-select
      v-model="_debugLevel"
      v-tooltip="'The level of of output to the log window can be specified.<br>For FMU setup use at least log level ON to check that model parameters are correctly updated.'"
      label="Debug level"
      :items="debugLevels"
    />
  </settings-panel>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'

interface DebugLevel {
  value: number
  text: string
}

@Component({
  components: {
    SettingsPanel,
  },
})
export default class LoggingSettings extends Vue {
  @Prop({ required: true })
  readonly debugLevel: number

  get debugLevels (): DebugLevel[] {
    return [
      { value: 0, text: 'Off' },
      { value: 1, text: 'On' },
      { value: 2, text: 'Verbose' },
      { value: 3, text: 'Very verbose' },
      { value: 4, text: 'For debugging only' },
    ]
  }

  get _debugLevel (): number { return this.debugLevel }
  set _debugLevel (level: number) { this.$emit('update:debugLevel', level) }
}
</script>

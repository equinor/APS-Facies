<template>
  <SettingsPanel title="FMU Settings">
    <v-col class="dense">
      <v-checkbox
        v-model="_runFmuWorkflows"
        label="Run FMU workflows"
      />
    </v-col>
    <div v-if="_runFmuWorkflows">
      <v-row
        no-gutters
      >
        <v-col
          class="pa-2"
          cols="3"
        >
          FMU Parameters List Location
        </v-col>
        <v-col
          class="pa-2"
          cols="5"
        >
          <v-text-field
            v-model="_fmuParameterListLocation"
            single-line
            solo
          />
        </v-col>
        <v-col
          class="pa-2"
          cols="4"
        >
          <bold-button
            title="Select Directory"
            @click="chooseFmuParametersFileLocation"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <numeric-field
            v-model="_maxLayersInFmu"
            :ranges="{ min: 0, max: Number.POSITIVE_INFINITY }"
            label="FMU grid depth"
            enforce-ranges
            @update:error="e => update('fmuGridDepth', e)"
          />
        </v-col>
        <v-col cols="6">
          <v-radio-group
            v-model="_importFields"
            row
            label="How are the Gaussian Random Fields calculated?"
          >
            <v-radio
              label="Simulated"
              value="generate"
            />
            <v-radio
              label="Imported"
              value="import"
            />
          </v-radio-group>
        </v-col>
      </v-row>
    </div>
  </SettingsPanel>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import rms from '@/api/rms'

import SettingsPanel from '@/components/dialogs/ProjectSettings/SettingsPanel.vue'
import BoldButton from '@/components/baseComponents/BoldButton.vue'
import NumericField from '@/components/selection/NumericField.vue'

interface Invalid {
  fmuGridDepth: boolean
}

type FieldUsage = 'generate' | 'import'

@Component({
  components: {
    SettingsPanel,
    NumericField,
    BoldButton,
  },
})
export default class FmuSettings extends Vue {
  invalid: Invalid = {
    fmuGridDepth: false
  }

  @Prop({ required: true, type: Boolean })
  readonly importFields: boolean

  @Prop({ required: true })
  readonly fmuParameterListLocation: string

  @Prop({ required: true, type: Boolean })
  readonly runFmuWorkflows: boolean

  @Prop({ required: true })
  readonly maxLayersInFmu: number

  get _fmuParameterListLocation (): string { return this.fmuParameterListLocation }
  set _fmuParameterListLocation (path: string) { this.$emit('update:fmuParameterListLocation', path) }

  get _runFmuWorkflows (): boolean { return this.runFmuWorkflows }
  set _runFmuWorkflows (toggled: boolean) { this.$emit('update:runFmuWorkflows', toggled) }

  get _maxLayersInFmu (): number { return this.maxLayersInFmu }
  set _maxLayersInFmu (value: number) { this.$emit('update:maxLayersInFmu', value) }

  get _importFields (): FieldUsage {
    if (this.importFields) return 'import'
    else return 'generate'
  }
  set _importFields (value: FieldUsage) {
    if (value === 'generate') this.$emit('update:importFields', false)
    else if (value === 'import') this.$emit('update:importFields', true)
    else throw Error(`Invalid value, '${value}'`)
  }

  chooseFmuParametersFileLocation () {
    rms.chooseDir('load').then((path: string): void => {
      if (path) {
        this._fmuParameterListLocation = path
      }
    })
  }

  update (type: string, value: boolean): void {
    Vue.set(this.invalid, type, value)
  }

  get hasErrors (): boolean { return Object.values(this.invalid).some(invalid => invalid) }

  @Watch('hasErrors', { deep: true })
  isInvalid (valid: boolean) {
    this.$emit('update:error', valid)
  }
}
</script>

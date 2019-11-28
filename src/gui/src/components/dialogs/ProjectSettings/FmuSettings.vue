<template>
  <SettingsPanel title="FMU Settings">
    <v-col class="dense">
      <v-checkbox
        v-model="_runFmuWorkflows"
        label="Run APS facies update in AHM/ERT"
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
          <v-popover
            trigger="hover"
            :disabled="hasGrid"
          >
            <v-combobox
              v-model="_fmuGrid"
              label="ERT/FMU simulation box grid"
              :disabled="!hasGrid"
              :items="fmuGrids"
            />
            <span slot="popover">No grid model has been selected</span>
          </v-popover>
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
        <v-col cols="12">
          <v-row
            v-if="!fmuGridExists"
          >
            <v-col cols="6">
              <span>The specified grid does not exist.</span>
              <v-checkbox
                v-model="_createFmuGrid"
                label="Do you want to create it?"
              />
            </v-col>
            <v-col cols="6">
              <numeric-field
                v-model="_maxLayersInFmu"
                :ranges="{ min: 0, max: Number.POSITIVE_INFINITY }"
                :disabled="!createFmuGrid"
                :required="createFmuGrid"
                label="Number of layers in FMU simulation box grid"
                enforce-ranges
                @update:error="e => update('fmuGridDepth', e)"
              />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </div>
  </SettingsPanel>
</template>

<script lang="ts">
import GridModel from '@/utils/domain/gridModel'
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import rms from '@/api/rms'

import SettingsPanel from '@/components/dialogs/ProjectSettings/SettingsPanel.vue'
import BoldButton from '@/components/baseComponents/BoldButton.vue'
import NumericField from '@/components/selection/NumericField.vue'

import { Store } from '@/store/typing'

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
  readonly fmuGrid: string

  @Prop({ required: true, type: Boolean })
  readonly createFmuGrid: boolean

  @Prop({ required: true })
  readonly maxLayersInFmu: number

  // @ts-ignore
  get _fmuGrid (): string { return this.fmuGrid }
  // @ts-ignore
  set _fmuGrid (value: string | { value: string }) {
    if (typeof (value) !== 'string') {
      value = value.value
    }
    this.$emit('update:fmuGrid', value)
  }

  get _createFmuGrid (): boolean { return this.createFmuGrid }
  set _createFmuGrid (value: boolean) { this.$emit('update:createFmuGrid', value) }

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
    if (type === 'fmuGridDepth') {
      value = value && !this.createFmuGrid
    }
    Vue.set(this.invalid, type, value)
  }

  get hasErrors (): boolean { return Object.values(this.invalid).some(invalid => invalid) }

  get hasGrid (): boolean { return !!this.$store.getters.gridModel }

  get fmuGridExists (): boolean {
    return this.availableGridModels
      .map(grid => grid.name)
      .includes(this._fmuGrid)
  }

  get availableGridModels (): GridModel[] { return Object.values((this.$store as Store).state.gridModels.available) }

  get fmuGrids () {
    const selectedGrid = this.$store.getters['gridModels/current']
    if (!selectedGrid) return []

    const dimension = selectedGrid.dimension
    return this.availableGridModels
      .map(grid => {
        return {
          value: grid.name,
          text: grid.name,
          disabled: !(
            grid.dimension.x === dimension.x
            && grid.dimension.y === dimension.y
          ),
        }
      })
  }

  @Watch('hasErrors', { deep: true })
  isInvalid (valid: boolean) {
    this.$emit('update:error', valid)
  }
}
</script>

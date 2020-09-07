<template>
  <settings-panel title="FMU Settings">
    <v-row
      no-gutters
    >
      <v-col class="dense">
        <warning-dialog
          ref="confirm"
          html
        />
        <base-tooltip
          :message="reasonForDisabling"
        >
          <v-checkbox
            v-model="_runFmuWorkflows"
            v-tooltip="'Enable updating of model parameters and Gaussian fields by FMU.'"
            label="Run APS facies update in AHM/ERT"
            :disabled="disableErtMode"
          />
        </base-tooltip>
      </v-col>
      <v-col>
        <v-checkbox
          v-model="_onlyUpdateFromFmu"
          v-tooltip="'Enable updating of model parameters by FMU but not Gaussian fields.'"
          label="Only run uncertainty update"
        />
      </v-col>
    </v-row>
    <div v-if="_runFmuWorkflows || _onlyUpdateFromFmu">
      <v-row
        v-if="!_onlyUpdateFromFmu"
      >
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
              @keydown.enter.stop="() => {/* Intentionally left blank, to stop event propagating to parent
               and closing the dialog, when enter is used to confirm the selected grid name */}"
            />
            <span slot="popover">No grid model has been selected</span>
          </v-popover>
        </v-col>
        <v-col cols="6">
          <v-radio-group
            v-model="_importFields"
            row
            label="Exchange of Gaussian Fields with FMU"
          >
            <v-radio
              label="Simulate and export to FMU"
              value="generate"
            />
            <v-radio
              label="Automatic select between Simulate/Export and Import"
              value="automatic_detect"
            />
          </v-radio-group>
          <v-row no-gutters>
            <v-select
              v-model="_fieldFileFormat"
              :items="fieldFileFormats"
              label="File format for export of Gaussian Random Fields"
            />
          </v-row>
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
                :ranges="{ min: minimumErtLayers, max: Number.POSITIVE_INFINITY }"
                :disabled="!createFmuGrid"
                :ignore-errors="!createFmuGrid"
                :required="createFmuGrid"
                label="Number of layers in FMU simulation box grid"
                @update:error="e => update('fmuGridDepth', e)"
              />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </div>
    <v-row no-gutters>
      <v-checkbox
       v-model="_exportFmuConfigFiles"
       v-tooltip="'When running this job from RMS workflow, APS model file and FMU config files are exported automatically.'"
       label="Export model file and FMU config files for current job."
       :disabled="!_runFmuWorkflows && !_onlyUpdateFromFmu"
      />
    </v-row>  
  </settings-panel>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'
import NumericField from '@/components/selection/NumericField.vue'
import WarningDialog from '@/components/dialogs/JobSettings/WarningDialog.vue'
import FileSelection from '@/components/selection/FileSelection.vue'
import BaseTooltip from '@/components/baseComponents/BaseTooltip.vue'

import { Store } from '@/store/typing'
import { ListItem } from '@/utils/typing'
import { DialogOptions } from '@/utils/domain/bases/interfaces'
import GridModel from '@/utils/domain/gridModel'

interface Invalid {
  fmuGridDepth: boolean
}

type FieldUsage = 'generate' | 'automatic_detect'

interface WarningParameters {
  toggled: boolean
  store: Store
  dialog: WarningDialog
}

function warn (dialog: WarningDialog, message: string, options: DialogOptions = { width: 450 }): void {
  dialog.open(
    'Be aware',
    message,
    options,
  )
}

function warnIfUsingCustomTrends ({ toggled, store, dialog }: WarningParameters): void {
  const affectedFields = Object.values(store.state.gaussianRandomFields.available)
    .filter(field => field.trend.type === 'RMS_PARAM')
  if (toggled && affectedFields.length > 0) {
    warn(dialog,
      `
<p>Some Gaussian Random Fields are using a custom Trend ('RMS_PARAM'), which is not supported in AHM-mode.</p>
<p>More specifically, these fields uses custom trends
<ul>
  ${affectedFields.map(({ name, parent }) => `<li>${name} in ${store.getters['zones/byParent'](parent)}</li>`)}
<ul>
</p>
`)
  }
}

@Component({
  components: {
    BaseTooltip,
    FileSelection,
    WarningDialog,
    SettingsPanel,
    NumericField,
  },
})
export default class FmuSettings extends Vue {
  invalid: Invalid = {
    fmuGridDepth: false
  }

  @Prop({ required: true, type: Boolean })
  readonly importFields: boolean

  @Prop({ required: true, type: Boolean })
  readonly runFmuWorkflows: boolean

  @Prop({ required: true, type: Boolean })
  readonly onlyUpdateFromFmu: boolean

  @Prop({ required: true })
  readonly fmuGrid: string

  @Prop({ required: true, type: Boolean })
  readonly createFmuGrid: boolean

  @Prop({ required: true })
  readonly maxLayersInFmu: number

  @Prop({ required: true })
  readonly fieldFileFormat: string

  @Prop({ required: true, type: Boolean })
  readonly exportFmuConfigFiles: boolean

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  get _fmuGrid (): string { return this.fmuGrid }
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  set _fmuGrid (value: string | { value: string }) {
    if (typeof (value) !== 'string') {
      value = value.value
    }
    this.$emit('update:fmuGrid', value)
  }

  get _onlyUpdateFromFmu (): boolean { return this.onlyUpdateFromFmu }
  set _onlyUpdateFromFmu (toggle: boolean) {
    this.$emit('update:onlyUpdateFromFmu', toggle)
    if (toggle) {
      this._runFmuWorkflows = false
    }
  }

  get _createFmuGrid (): boolean { return this.createFmuGrid }
  set _createFmuGrid (value: boolean) { this.$emit('update:createFmuGrid', value) }

  get _runFmuWorkflows (): boolean { return this.runFmuWorkflows }
  set _runFmuWorkflows (toggled: boolean) {
    const params = { toggled, store: this.$store, dialog: (this.$refs.confirm as WarningDialog) }
    warnIfUsingCustomTrends(params)
    this.$emit('update:runFmuWorkflows', toggled)
    if (toggled) {
      this._onlyUpdateFromFmu = false
    }
  }

  get _maxLayersInFmu (): number { return this.maxLayersInFmu }
  set _maxLayersInFmu (value: number) { this.$emit('update:maxLayersInFmu', value) }

  get minimumErtLayers (): number { return (this.$store as Store).state.fmu.maxDepth.minimum }

  get _importFields (): FieldUsage {
    if (this.importFields) return 'automatic_detect'
    else return 'generate'
  }

  set _importFields (value: FieldUsage) {
    if (value === 'generate') this.$emit('update:importFields', false)
    else if (value === 'automatic_detect') this.$emit('update:importFields', true)
    else throw Error(`Invalid value, '${value}'`)
  }

  get _fieldFileFormat (): string { return this.fieldFileFormat }
  set _fieldFileFormat (format: string) { this.$emit('update:fieldFileFormat', format) }

  get fieldFileFormats (): string[] { return this.$store.state.fmu.fieldFileFormat.legal }

  get _exportFmuConfigFiles (): boolean { return this.exportFmuConfigFiles }
  set _exportFmuConfigFiles (toggle: boolean) {
    this.$emit('update:exportFmuConfigFiles', toggle)
  }

  update (type: string, value: boolean): void {
    if (type === 'fmuGridDepth') {
      value = value && this.createFmuGrid
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

  get fmuGrids (): ListItem<string>[] {
    const selectedGrid = (this.$store as Store).getters['gridModels/current']
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
            && grid.dimension.z >= this.minimumErtLayers
            && grid.name !== selectedGrid.name
            && grid.zones === 1
          ),
        }
      })
  }

  @Watch('hasErrors', { deep: true })
  isInvalid (valid: boolean): void {
    this.$emit('update:error', valid)
  }

  // Settings for handling regions, and ERT-mode
  // These should not be needed when regions are supported in ERT-mode
  get reasonForDisabling (): string | undefined {
    if (this.useRegions) {
      return 'Regions are not supported in ERT/AHM mode. Please deselect regions if you want to run APS with ERT/AHM'
    } else if (this.gridHasReverseFaults) {
      return 'Grids with reverse faults, are not supported in ERT mode'
    }
    return undefined
  }

  get useRegions (): boolean { return (this.$store as Store).state.regions.use }

  get gridHasReverseFaults (): boolean {
    const grid = (this.$store as Store).getters['gridModels/current']
    return !!grid && grid.hasDualIndexSystem
  }

  get disableErtMode (): boolean { return !!this.reasonForDisabling }
}
</script>

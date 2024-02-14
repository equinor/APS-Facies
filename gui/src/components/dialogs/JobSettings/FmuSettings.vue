<template>
  <settings-panel title="FMU Settings">
    <v-row no-gutters>
      <v-col class="dense">
        <warning-dialog ref="confirm" html />
        <v-checkbox
          v-model="_runFmuWorkflows"
          v-tooltip="
            'Enable updating of model parameters and Gaussian fields by FMU.'
          "
          label="Run APS facies update in AHM/ERT"
        />
      </v-col>
      <v-col>
        <v-checkbox
          v-model="_onlyUpdateFromFmu"
          v-tooltip="
            'Enable updating of model parameters by FMU but not Gaussian fields.'
          "
          label="Only run uncertainty update"
        />
      </v-col>
    </v-row>
    <div v-if="_runFmuWorkflows || _onlyUpdateFromFmu">
      <v-row v-if="!_onlyUpdateFromFmu">
        <v-col cols="6">
          <floating-tooltip trigger="hover" :disabled="hasGrid">
            <v-combobox
              v-model="_fmuGrid"
              label="ERT/FMU simulation box grid"
              :disabled="!hasGrid"
              :items="fmuGrids"
              @keydown.enter.stop="
                () => {
                  /* Intentionally left blank, to stop event propagating to parent
               and closing the dialog, when enter is used to confirm the selected grid name */
                }
              "
            />
            <template #popper>No grid model has been selected</template>
          </floating-tooltip>
          <v-row v-if="!fmuGridExists">
            <v-col cols="6">
              <span>The specified grid does not exist.</span>
              <v-checkbox
                v-model="_createFmuGrid"
                label="Do you want to create it?"
              />
              <numeric-field
                v-model="_maxLayersInFmu"
                :ranges="{
                  min: minimumErtLayers,
                  max: Number.POSITIVE_INFINITY,
                }"
                :disabled="!createFmuGrid"
                :ignore-errors="!createFmuGrid"
                :required="createFmuGrid"
                label="Number of layers in ERTBOX grid"
                @update:error="(e) => update('fmuGridDepth', e)"
              />
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="6">
          <v-radio-group
            v-model="_importFields"
            inline
            label="Exchange of Gaussian Fields with FMU"
          >
            <v-radio label="Simulate and export to FMU" value="generate" />
            <v-radio
              v-tooltip="
                'Use this option in assisted history matching with ERT.'
              "
              label="Automatic select between Simulate/Export and Import"
              value="automatic_detect"
            />
          </v-radio-group>
          <v-row no-gutters>
            <v-select
              v-model="_fieldFileFormat"
              :items="FIELD_FORMATS"
              label="File format for export of Gaussian Random Fields"
              variant="underlined"
            />
          </v-row>
          <v-row no-gutters>
            <v-select
              v-model="_customTrendExtrapolationMethod"
              v-tooltip="
                'Extrapolation method for custom trends to fill undefined grid cells in ERT/FMU grid.'
              "
              :items="TREND_EXTRAPOLATION_METHODS"
              :disabled="!hasRmsParamTrend"
              label="RMS_PARAM trend extrapolation method for ERT/FMU grid."
              variant="underlined"
            />
          </v-row>
          <v-row no-gutters>
            <v-checkbox
              v-model="_onlyUpdateResidualFields"
              v-tooltip="
                'Export/Import only the Gaussian Residual for GRF with trend to/from ERT. The trend part of the GRF is added by APS before applying truncation rule. '
              "
              label="For GRF with trend let ERT only update the residual field."
              :disabled="!_runFmuWorkflows"
            />
          </v-row>
        </v-col>
      </v-row>
      <v-col cols="6">
        <v-row no-gutters>
          <v-checkbox
            v-model="_exportFmuConfigFiles"
            v-tooltip="
              'When running this job from RMS workflow, FMU config and template files with APS parameters are exported automatically.'
            "
            label="Export APS model and FMU config files."
            :disabled="!_runFmuWorkflows && !_onlyUpdateFromFmu"
          />
          <v-checkbox
            v-model="_useNonStandardFmu"
            v-tooltip="
              'Use non-standard customized settings for FMU files and directories. File .aps_config will be used. '
            "
            label="Use non-standard FMU files and directory structure."
            :disabled="!_runFmuWorkflows && !_onlyUpdateFromFmu"
          />
        </v-row>
      </v-col>
    </div>
  </settings-panel>
</template>

<script setup lang="ts">
import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'
import NumericField from '@/components/selection/NumericField.vue'
import WarningDialog from '@/components/dialogs/JobSettings/WarningDialog.vue'
import { useStore } from '../../../store'
import { computed, ref, watch } from 'vue'
import {
  FIELD_FORMATS,
  type FieldFormats,
  TREND_EXTRAPOLATION_METHODS,
} from '@/stores/fmu/options'

interface Invalid {
  fmuGridDepth: boolean
}

type FieldUsage = 'generate' | 'automatic_detect'

type Props = {
  importFields: boolean
  runFmuWorkflows: boolean
  onlyUpdateFromFmu: boolean
  fmuGrid: string
  createFmuGrid: boolean
  maxLayersInFmu: number | null
  fieldFileFormat: FieldFormats
  customTrendExtrapolationMethod: string
  exportFmuConfigFiles: boolean
  onlyUpdateResidualFields: boolean
  useNonStandardFmu: boolean
  exportErtBoxGrid: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (event: 'update:importFields', value: boolean): void
  (event: 'update:runFmuWorkflows', value: boolean): void
  (event: 'update:onlyUpdateFromFmu', value: boolean): void
  (event: 'update:fmuGrid', value: string): void
  (event: 'update:createFmuGrid', value: boolean): void
  (event: 'update:maxLayersInFmu', value: number): void
  (event: 'update:fieldFileFormat', value: FieldFormats): void
  (event: 'update:customTrendExtrapolationMethod', value: string): void
  (event: 'update:exportFmuConfigFiles', value: boolean): void
  (event: 'update:onlyUpdateResidualFields', value: boolean): void
  (event: 'update:useNonStandardFmu', value: boolean): void
  (event: 'update:exportErtBoxGrid', value: boolean): void
  (event: 'update:error', error: boolean): void
}>()

const store = useStore()
const minimumErtLayers = computed(() => store.state.fmu.maxDepth.minimum)
const availableGridModels = computed(() =>
  Object.values(store.state.gridModels.available),
)
const invalid = ref<Invalid>({
  fmuGridDepth: false,
})

const hasErrors = computed(() => {
  return Object.values(invalid.value).some((invalid) => invalid)
})
watch(hasErrors, (value: boolean) => emit('update:error', value))

const _fmuGrid = computed({
  get: () => props.fmuGrid,
  set: (value: string | { value: string }) => {
    const newValue = typeof value === 'string' ? value : value.value
    emit('update:fmuGrid', newValue)
  },
})

const _onlyUpdateFromFmu = computed({
  get: () => props.onlyUpdateFromFmu,
  set: (toggled: boolean) => {
    emit('update:onlyUpdateFromFmu', toggled)
    if (toggled) {
      // _onlyUpdateFromFmu and _runFmuWorkflows are mutually exclusive
      _runFmuWorkflows.value = false
    }
  },
})

const _createFmuGrid = computed({
  get: () => props.createFmuGrid,
  set: (value: boolean) => emit('update:createFmuGrid', value),
})

const _runFmuWorkflows = computed({
  get: () => props.runFmuWorkflows,
  set: (toggled: boolean) => {
    emit('update:runFmuWorkflows', toggled)
    if (toggled) {
      // _runFmuWorkflows and _onlyUpdateFromFmu are mutually exclusive
      _onlyUpdateFromFmu.value = false
    }
  },
})

const _maxLayersInFmu = computed({
  get: () => props.maxLayersInFmu ?? 12,
  set: (value: number) => emit('update:maxLayersInFmu', value),
})

const _importFields = computed({
  get: () => (props.importFields ? 'automatic_detect' : 'generate'),
  set: (value: FieldUsage) =>
    emit('update:importFields', value === 'automatic_detect'),
})

const _fieldFileFormat = computed<FieldFormats>({
  get: () => props.fieldFileFormat,
  set: (value: FieldFormats) => emit('update:fieldFileFormat', value),
})

const _customTrendExtrapolationMethod = computed({
  get: () => props.customTrendExtrapolationMethod,
  set: (value: string) => emit('update:customTrendExtrapolationMethod', value),
})

const _exportFmuConfigFiles = computed({
  get: () => props.exportFmuConfigFiles,
  set: (value: boolean) => emit('update:exportFmuConfigFiles', value),
})

const _onlyUpdateResidualFields = computed({
  get: () => props.onlyUpdateResidualFields,
  set: (toggle: boolean) => {
    emit('update:onlyUpdateResidualFields', toggle)
  },
})

const _useNonStandardFmu = computed({
  get: () => props.useNonStandardFmu,
  set: (value: boolean) => emit('update:useNonStandardFmu', value),
})

function update(type: keyof Invalid, value: boolean): void {
  if (type === 'fmuGridDepth') {
    value = value && props.createFmuGrid
  }
  invalid.value[type] = value
}

const hasGrid = computed(() => {
  return !!store.getters.gridModel
})

const hasRmsParamTrend = computed(() => {
  const affectedFields = Object.values(
    store.state.gaussianRandomFields.available,
  ).filter((field) => field.trend.type === 'RMS_PARAM')
  return affectedFields.length > 0
})

const fmuGridExists = computed(() => {
  return availableGridModels.value
    .map((grid) => grid.name)
    .includes(_fmuGrid.value)
})

const fmuGrids = computed(() => {
  const selectedGrid = store.getters['gridModels/current']
  if (!selectedGrid) return []

  const dimension = selectedGrid.dimension
  return availableGridModels.value.map((grid) => {
    return {
      value: grid.name,
      title: grid.name,
      props: {
        disabled: !(
          grid.dimension.x === dimension.x &&
          grid.dimension.y === dimension.y &&
          grid.dimension.z >= minimumErtLayers.value &&
          grid.name !== selectedGrid.name &&
          grid.zones === 1
        ),
      }
    }
  })
})
</script>

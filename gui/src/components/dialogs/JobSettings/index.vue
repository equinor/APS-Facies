<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="800"
    scrollable
    @keydown.esc="cancel"
    @keydown.enter="
      () => {
        if (!hasErrors) ok
      }
    "
  >
    <template #activator="{ props }">
      <v-btn color="primary" v-bind="props" variant="outlined"> Job Settings </v-btn>
    </template>
    <v-card>
      <v-card-title class="text-h5" />
      <v-card-text>
        <fmu-settings
          v-model:run-fmu-workflows="runFmuWorkflows"
          v-model:only-update-from-fmu="onlyUpdateFromFmu"
          v-model:max-layers-in-fmu="maxLayersInFmu"
          v-model:import-fields="importFields"
          v-model:fmu-grid="fmuGrid"
          v-model:create-fmu-grid="createFmuGrid"
          v-model:field-file-format="fieldFileFormat as FieldFormats"
          v-model:custom-trend-extrapolation-method="
            customTrendExtrapolationMethod
          "
          v-model:export-fmu-config-files="exportFmuConfigFiles"
          v-model:only-update-residual-fields="onlyUpdateResidualFields"
          v-model:use-non-standard-fmu="useNonStandardFmu"
          v-model:export-ert-box-grid="exportErtBoxGrid"
          @update:error="(e) => update('fmu', e)"
        />
        <br />
        <logging-settings v-model:debug-level="debugLevel" />
        <br />
        <transformtype-settings v-model:transform-type="transformType" />
        <br />
        <run-settings
          v-model:max-allowed-fraction-of-values-outside-tolerance="
            maxAllowedFractionOfValuesOutsideTolerance
          "
          v-model:tolerance-of-probability-normalisation="
            toleranceOfProbabilityNormalisation
          "
        />
        <br />
        <settings-panel title="Display Settings">
          <v-row no-gutters>
            <v-col cols="8">
              <v-row no-gutters>
                <v-col class="pa-2">
                  <v-radio-group
                    v-model="showZoneNameNumber"
                    column
                    label="Show:"
                  >
                    <v-radio label="Zone Name" value="name" />
                    <v-radio label="Zone Number" value="number" />
                  </v-radio-group>
                </v-col>
                <v-col class="pa-2">
                  <v-radio-group
                    v-model="showRegionNameNumber"
                    colum
                    label="Show:"
                  >
                    <v-radio label="Region Name" value="name" />
                    <v-radio label="Region Number" value="number" />
                  </v-radio-group>
                </v-col>
              </v-row>
              <v-row class="pa-2">
                <v-col md="6">
                  <v-select
                    v-model="colorScale"
                    label="Color scale of Gaussian Random Fields"
                    :items="COLOR_SCALES"
                    variant="underlined"
                  />
                </v-col>
                <v-col md="6">
                  <v-select
                    v-model="faciesColorLibrary"
                    label="The color library for Facies"
                    :items="stores.constants.faciesColors.libraries"
                    variant="underlined"
                  >
                    <template #item="{ item, props }">
                      <v-list-item v-bind="props">
                        <br>
                        <v-row>
                          <v-col
                            v-for="color in item.value.colors"
                            :key="color"
                            class="pa-2"
                            :style="{ backgroundColor: color }"
                          />
                        </v-row>
                      </v-list-item>
                    </template>
                  </v-select>
                </v-col>
              </v-row>
            </v-col>
            <v-col class="dense">
              <v-col class="dense">
                <v-checkbox
                  v-model="automaticAlphaFieldSelection"
                  label="Automatic assign GRF to each Alpha coordinate"
                />
              </v-col>
              <v-col class="dense">
                <v-checkbox
                  v-model="automaticObservedFaciesSelection"
                  label="Automatically select facies observed in well logs"
                />
              </v-col>
              <v-col class="dense">
                <v-checkbox
                  v-model="automaticFaciesFill"
                  label="Automatically assign facies to templates"
                />
              </v-col>
              <v-col class="dense">
                <v-checkbox
                  v-model="filterZeroProbability"
                  label="Ignore Facies with 0 probability"
                />
              </v-col>
            </v-col>
          </v-row>
        </settings-panel>
        <br>
        <grid-information />
      </v-card-text>
      <v-card-actions>
        {{ version && `Version: ${version}` }}
        <v-spacer />
        <bold-button title="Cancel" @click="cancel" />
        <bold-button
          title="Ok"
          :disabled="hasErrors"
          :tooltip-text="hasErrors ? 'Some value(s) are invalid' : undefined"
          @click="ok"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import rms from '@/api/rms'
import LoggingSettings from '@/components/dialogs/JobSettings/LoggingSettings.vue'
import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'
import BoldButton from '@/components/baseComponents/BoldButton.vue'
import FmuSettings from '@/components/dialogs/JobSettings/FmuSettings.vue'
import RunSettings from '@/components/dialogs/JobSettings/RunSettings.vue'
import GridInformation from '@/components/dialogs/JobSettings/GridInformation.vue'
import TransformtypeSettings from '@/components/dialogs/JobSettings/TransformtypeSettings.vue'

import type ColorLibrary from '@/utils/domain/colorLibrary'
import type { Optional } from '@/utils/typing'
import { ref, computed, watch } from 'vue'
import type { NameOrNumber } from '@/stores/options'
import { useOptionStore } from '@/stores/options'
import type {
  FieldFormats,
  TrendExtrapolationMethod
} from '@/stores/fmu/options'
import {
  useFmuOptionStore,
} from '@/stores/fmu/options'
import { useFmuMaxDepthStore } from '@/stores/fmu/maxDepth'
import { useParameterDebugLevelStore } from '@/stores/parameters/debug-level'
import { type TransformType, useParameterTransformTypeStore } from '@/stores/parameters/transform-type'
import {
  useParametersMaxFractionOfValuesOutsideToleranceStore,
  useParametersToleranceOfProbabilityNormalisationStore,
} from '@/stores/parameters/tolerance'
import { useConstantsFaciesColorsStore } from '@/stores/constants/facies-colors'
import type { AllowedColorScales } from '@/config'
import { COLOR_SCALES } from '@/config'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { useGridModelStore } from '@/stores/grid-models'
import { VSelect } from 'vuetify/components'

const stores = {
  gridModel: useGridModelStore(),
  options: useOptionStore(),
  gaussianRandomField: useGaussianRandomFieldStore(),
  fmu: {
    options: useFmuOptionStore(),
    maxDepth: useFmuMaxDepthStore(),
  },
  parameter: {
    transformType: useParameterTransformTypeStore(),
    debugLevel: useParameterDebugLevelStore(),
    maxFractionOfValuesOutsideTolerance: useParametersMaxFractionOfValuesOutsideToleranceStore(),
    toleranceOfProbabilityNormalisation: useParametersToleranceOfProbabilityNormalisationStore(),
  },
  constants: {
    faciesColors: useConstantsFaciesColorsStore()
  }
}

type Invalid = { fmu: boolean }
const invalid = ref<Invalid>({ fmu: false })

const dialog = ref(false)
const showZoneNameNumber = ref('')
const showRegionNameNumber = ref('')
const automaticAlphaFieldSelection = ref(false)
const automaticFaciesFill = ref(false)
const automaticObservedFaciesSelection = ref(false)
const filterZeroProbability = ref(false)
const runFmuWorkflows = ref(false)
const colorScale = ref<AllowedColorScales | null | undefined>(null)
const faciesColorLibrary = ref<Optional<ColorLibrary>>(null)
const maxLayersInFmu = ref<number | null>(0)
const debugLevel = ref<0 | 1 | 2 | 3 | 4>(0)
const transformType = ref(0)
const importFields = ref(false)
const fmuGrid = ref('')
const createFmuGrid = ref(false)
const onlyUpdateFromFmu = ref(false)
const maxAllowedFractionOfValuesOutsideTolerance = ref(0)
const toleranceOfProbabilityNormalisation = ref(0)
const fieldFileFormat = ref<FieldFormats | null>(null)
const customTrendExtrapolationMethod = ref('')
const exportFmuConfigFiles = ref(false)
const useNonStandardFmu = ref(false)
const onlyUpdateResidualFields = ref(false)
const exportErtBoxGrid = ref(true)

const version = computed<string>(
  () => import.meta.env.VUE_APP_APS_VERSION || '',
)
const currentGridModel = computed(() => stores.gridModel.current)

const currentGridModelName = computed(() => currentGridModel.value?.name)

const hasErrors = computed(() =>
  Object.values(invalid.value).some((invalid) => invalid),
)

function cancel(): void {
  dialog.value = false
}

watch(dialog, (value: boolean) => {
  if (!value) return
  const options = stores.options.options
  const fmu = stores.fmu.options.options
  const fmuMaxDepth = stores.fmu.maxDepth.maxDepth

  maxLayersInFmu.value = fmuMaxDepth.value
  runFmuWorkflows.value = fmu.runFmuWorkflows
  onlyUpdateFromFmu.value = fmu.onlyUpdateFromFmu
  fmuGrid.value = fmu.simulationGrid
  createFmuGrid.value = fmu.create
  fieldFileFormat.value = fmu.fieldFileFormat
  customTrendExtrapolationMethod.value = fmu.customTrendExtrapolationMethod
  onlyUpdateResidualFields.value = fmu.onlyUpdateResidualFields
  useNonStandardFmu.value = fmu.useNonStandardFmu
  exportErtBoxGrid.value = fmu.exportErtBoxGrid

  debugLevel.value = stores.parameter.debugLevel.level
  transformType.value = stores.parameter.transformType.level
  maxAllowedFractionOfValuesOutsideTolerance.value =
    stores.parameter.maxFractionOfValuesOutsideTolerance.tolerance
  toleranceOfProbabilityNormalisation.value =
    stores.parameter.toleranceOfProbabilityNormalisation.tolerance
  showZoneNameNumber.value = options.showNameOrNumber.zone
  showRegionNameNumber.value = options.showNameOrNumber.region
  automaticAlphaFieldSelection.value = options.automaticAlphaFieldSelection
  automaticObservedFaciesSelection.value =
    options.automaticObservedFaciesSelection
  automaticFaciesFill.value = options.automaticFaciesFill
  filterZeroProbability.value = options.filterZeroProbability
  importFields.value = options.importFields
  exportFmuConfigFiles.value = options.exportFmuConfigFiles
  colorScale.value = options.colorScale
  faciesColorLibrary.value = stores.constants.faciesColors.current
})

async function ok(): Promise<void> {
  stores.parameter.debugLevel.select(debugLevel.value)
  stores.parameter.transformType.select(transformType.value as TransformType)
  stores.parameter.maxFractionOfValuesOutsideTolerance.setTolerance(
    maxAllowedFractionOfValuesOutsideTolerance.value,
  )
  stores.parameter.toleranceOfProbabilityNormalisation.setTolerance(
    toleranceOfProbabilityNormalisation.value,
  )
  stores.fmu.maxDepth.set(maxLayersInFmu.value)
  stores.fmu.options.populate({
    runFmuWorkflows: runFmuWorkflows.value,
    onlyUpdateFromFmu: onlyUpdateFromFmu.value,
    simulationGrid: fmuGrid.value,
    create: createFmuGrid.value,
    fieldFileFormat: fieldFileFormat.value as FieldFormats,
    useNonStandardFmu: useNonStandardFmu.value,
    exportErtBoxGrid: exportErtBoxGrid.value,
    customTrendExtrapolationMethod:
      customTrendExtrapolationMethod.value as TrendExtrapolationMethod,
    onlyUpdateResidualFields: onlyUpdateResidualFields.value,
  })

  stores.options.populate({
    showNameOrNumber: {
      zone: showZoneNameNumber.value as NameOrNumber,
      region: showRegionNameNumber.value as NameOrNumber,
    },
    automaticAlphaFieldSelection: automaticAlphaFieldSelection.value,
    automaticObservedFaciesSelection: automaticObservedFaciesSelection.value,
    automaticFaciesFill: automaticFaciesFill.value,
    filterZeroProbability: filterZeroProbability.value,
    importFields: importFields.value,
    exportFmuConfigFiles: exportFmuConfigFiles.value,
    colorScale: colorScale.value as AllowedColorScales,
  })

  stores.constants.faciesColors.set(faciesColorLibrary.value as ColorLibrary)

  // Create ERTBOX grid if createFmuGrid.value is true
  if (runFmuWorkflows.value && createFmuGrid.value) {
    if (!currentGridModelName.value) throw new Error('No grid model name selected')
    await rms.createErtBoxGrid(
      currentGridModelName.value as string,
      fmuGrid.value,
      maxLayersInFmu.value,
      debugLevel.value,
    )
    createFmuGrid.value = false
    stores.fmu.options.options.create = createFmuGrid.value

    await useGridModelStore().refresh()
  }

  // Create the .aps_config file if useNonStandardFmu.value is true and it does not exist already
  await rms.createAPSFmuConfigFile(useNonStandardFmu.value)

  dialog.value = false
}

function update(type: keyof Invalid, value: boolean): void {
  invalid.value[type] = value
}
</script>

<style lang="scss" scoped>
input[type='text'] {
  border: 2px solid blue;
  border-radius: 4px;
}
</style>

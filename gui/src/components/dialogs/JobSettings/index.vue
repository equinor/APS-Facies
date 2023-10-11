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
      <v-btn outlined color="primary" dark v-bind="props"> Job Settings </v-btn>
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
          v-model:field-file-format="fieldFileFormat"
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
                    :items="store.state.options.colorScale.legal"
                  />
                </v-col>
                <v-col md="6">
                  <v-select
                    v-model="faciesColorLibrary"
                    label="The color library for Facies"
                    :items="store.getters['constants/faciesColors/libraries']"
                  >
                    <template #item="{ item, props }">
                      <v-col @click="props.onClick(item.value)">
                        <v-row>
                          <v-col cols="12">
                            {{ item.title }}
                          </v-col>
                          <v-col
                            v-for="color in item.value.colors"
                            :key="color"
                            class="pa-2"
                            :style="{ backgroundColor: color }"
                          />
                        </v-row>
                      </v-col>
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
        <br />
        <grid-information
          :grid-size="gridSize"
          :simulation-settings="simulationSettings"
        />
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

import ColorLibrary from '@/utils/domain/colorLibrary'
import { Optional } from '@/utils/typing'
import { Store } from '@/store/typing'
import {
  Coordinate3D,
  SimulationSettings,
} from '@/utils/domain/bases/interfaces'
import { ref, computed, watch } from 'vue'
import { useStore } from '../../../store'

const store = useStore()

interface Invalid {
  fmu: boolean
}
const invalid = ref<Invalid>({
  fmu: false,
})

const dialog = ref(false)
const showZoneNameNumber = ref('')
const showRegionNameNumber = ref('')
const automaticAlphaFieldSelection = ref(false)
const automaticFaciesFill = ref(false)
const automaticObservedFaciesSelection = ref(false)
const filterZeroProbability = ref(false)
const runFmuWorkflows = ref(false)
const colorScale = ref('')
const faciesColorLibrary = ref<Optional<ColorLibrary>>(null)
const maxLayersInFmu = ref<number>(0)
const debugLevel = ref<0 | 1 | 2 | 3 | 4>(0)
const transformType = ref(0)
const importFields = ref(false)
const fmuGrid = ref('')
const createFmuGrid = ref(false)
const onlyUpdateFromFmu = ref(false)
const maxAllowedFractionOfValuesOutsideTolerance = ref(0)
const toleranceOfProbabilityNormalisation = ref(0)
const fieldFileFormat = ref('')
const customTrendExtrapolationMethod = ref('')
const exportFmuConfigFiles = ref(false)
const useNonStandardFmu = ref(false)
const onlyUpdateResidualFields = ref(false)
const exportErtBoxGrid = ref(true)

const simulationSettings = computed<SimulationSettings>(() =>
  store.getters.simulationSettings(),
)
const gridSize = computed<Coordinate3D>(() => simulationSettings.value.gridSize)
const version = computed<string>(
  () => import.meta.env.VUE_APP_APS_VERSION || '',
)
const currentGridModel = computed<string>(() => store.getters.gridModel)

const hasErrors = computed(() =>
  Object.values(invalid.value).some((invalid) => invalid),
)

function cancel(): void {
  dialog.value = false
}

watch(dialog, (value: boolean) => {
  if (!value) return
  const options = (store as Store).state.options
  const parameters = store.state.parameters
  const fmu = store.state.fmu

  maxLayersInFmu.value = fmu.maxDepth.value
  runFmuWorkflows.value = fmu.runFmuWorkflows.value
  onlyUpdateFromFmu.value = fmu.onlyUpdateFromFmu.value
  fmuGrid.value = fmu.simulationGrid.current
  createFmuGrid.value = fmu.create.value
  fieldFileFormat.value = fmu.fieldFileFormat.value
  customTrendExtrapolationMethod.value =
    fmu.customTrendExtrapolationMethod.value
  onlyUpdateResidualFields.value = fmu.onlyUpdateResidualFields.value
  useNonStandardFmu.value = fmu.useNonStandardFmu.value
  exportErtBoxGrid.value = fmu.exportErtBoxGrid.value

  debugLevel.value = parameters.debugLevel.selected
  transformType.value = parameters.transformType.selected
  maxAllowedFractionOfValuesOutsideTolerance.value =
    parameters.maxAllowedFractionOfValuesOutsideTolerance.selected
  toleranceOfProbabilityNormalisation.value =
    parameters.toleranceOfProbabilityNormalisation.selected
  showZoneNameNumber.value = options.showNameOrNumber.zone.value
  showRegionNameNumber.value = options.showNameOrNumber.region.value
  automaticAlphaFieldSelection.value =
    options.automaticAlphaFieldSelection.value
  automaticObservedFaciesSelection.value =
    options.automaticObservedFaciesSelection.value
  automaticFaciesFill.value = options.automaticFaciesFill.value
  filterZeroProbability.value = options.filterZeroProbability.value
  importFields.value = options.importFields.value
  exportFmuConfigFiles.value = options.exportFmuConfigFiles.value
  colorScale.value = options.colorScale.value
  faciesColorLibrary.value = store.getters['constants/faciesColors/current']
})

async function ok(): Promise<void> {
  const dispatch = store.dispatch
  await Promise.all([
    dispatch('parameters/debugLevel/select', debugLevel.value),
    dispatch('parameters/transformType/select', transformType.value),
    dispatch(
      'parameters/maxAllowedFractionOfValuesOutsideTolerance/select',
      maxAllowedFractionOfValuesOutsideTolerance.value,
    ),
    dispatch(
      'parameters/toleranceOfProbabilityNormalisation/select',
      toleranceOfProbabilityNormalisation.value,
    ),
    dispatch('fmu/maxDepth/set', maxLayersInFmu.value),
    dispatch('fmu/runFmuWorkflows/set', runFmuWorkflows.value),
    dispatch('fmu/onlyUpdateFromFmu/set', onlyUpdateFromFmu.value),
    dispatch('fmu/simulationGrid/set', fmuGrid.value),
    dispatch('fmu/create/set', createFmuGrid.value),
    dispatch('fmu/fieldFileFormat/set', fieldFileFormat.value),
    dispatch(
      'fmu/customTrendExtrapolationMethod/set',
      customTrendExtrapolationMethod.value,
    ),
    dispatch(
      'fmu/onlyUpdateResidualFields/set',
      onlyUpdateResidualFields.value,
    ),
    dispatch('fmu/useNonStandardFmu/set', useNonStandardFmu.value),
    dispatch('fmu/exportErtBoxGrid/set', exportErtBoxGrid.value),

    dispatch('options/showNameOrNumber/zone/set', showZoneNameNumber.value),
    dispatch('options/showNameOrNumber/region/set', showRegionNameNumber.value),
    dispatch(
      'options/automaticAlphaFieldSelection/set',
      automaticAlphaFieldSelection.value,
    ),
    dispatch(
      'options/automaticObservedFaciesSelection/set',
      automaticObservedFaciesSelection.value,
    ),
    dispatch('options/automaticFaciesFill/set', automaticFaciesFill.value),
    dispatch('options/filterZeroProbability/set', filterZeroProbability.value),
    dispatch('options/importFields/set', importFields.value),
    dispatch('options/exportFmuConfigFiles/set', exportFmuConfigFiles.value),
    dispatch('options/colorScale/set', colorScale.value),

    dispatch('constants/faciesColors/set', faciesColorLibrary.value),
  ])
  // Create ERTBOX grid if createFmuGrid.value is true
  if (createFmuGrid.value) {
    rms.createErtBoxGrid(
      currentGridModel.value,
      fmuGrid.value,
      maxLayersInFmu.value,
      debugLevel.value,
    )
    createFmuGrid.value = false
    await Promise.all([
      dispatch('fmu/create/set', createFmuGrid.value),
      dispatch('gridModels/refresh'),
    ])
  }

  // Create the .aps_config file if useNonStandardFmu.value is true and it does not exist already
  await rms.createAPSFmuConfigFile(useNonStandardFmu.value)

  dialog.value = false
}

function update(type: string, value: boolean): void {
  invalid.value[type] = value
}
</script>

<style lang="scss" scoped>
input[type='text'] {
  border: 2px solid blue;
  border-radius: 4px;
}
</style>

<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="800"
    scrollable
    @keydown.esc="cancel"
    @keydown.enter="() => {if (!hasErrors) ok}"
  >
    <template #activator="{ on }">
      <v-btn
        outlined
        color="primary"
        dark
        v-on="on"
      >
        Job Settings
      </v-btn>
    </template>
    <v-card>
      <v-card-title
        class="text-h5"
      />
      <v-card-text>
        <fmu-settings
          :run-fmu-workflows.sync="runFmuWorkflows"
          :only-update-from-fmu.sync="onlyUpdateFromFmu"
          :max-layers-in-fmu.sync="maxLayersInFmu"
          :import-fields.sync="importFields"
          :fmu-grid.sync="fmuGrid"
          :create-fmu-grid.sync="createFmuGrid"
          :field-file-format.sync="fieldFileFormat"
          :custom-trend-extrapolation-method.sync="customTrendExtrapolationMethod"
          :export-fmu-config-files.sync="exportFmuConfigFiles"
          :only-update-residual-fields.sync="onlyUpdateResidualFields"
          @update:error="e => update('fmu', e)"
        />
        <br>
        <logging-settings
          :debug-level.sync="debugLevel"
        />
        <br>
        <transformtype-settings
          :transform-type.sync="transformType"
        />
        <br>
        <run-settings
          :max-allowed-fraction-of-values-outside-tolerance.sync="maxAllowedFractionOfValuesOutsideTolerance"
          :tolerance-of-probability-normalisation.sync="toleranceOfProbabilityNormalisation"
        />
        <br>
        <settings-panel title="Display Settings">
          <v-row
            no-gutters
          >
            <v-col cols="8">
              <v-row no-gutters>
                <v-col
                  class="pa-2"
                >
                  <v-radio-group
                    v-model="showZoneNameNumber"
                    column
                    label="Show:"
                  >
                    <v-radio
                      label="Zone Name"
                      value="name"
                    />
                    <v-radio
                      label="Zone Number"
                      value="number"
                    />
                  </v-radio-group>
                </v-col>
                <v-col
                  class="pa-2"
                >
                  <v-radio-group
                    v-model="showRegionNameNumber"
                    colum
                    label="Show:"
                  >
                    <v-radio
                      label="Region Name"
                      value="name"
                    />
                    <v-radio
                      label="Region Number"
                      value="number"
                    />
                  </v-radio-group>
                </v-col>
              </v-row>
              <v-row
                class="pa-2"
              >
                <v-col
                  md="6"
                >
                  <v-select
                    v-model="colorScale"
                    label="Color scale of Gaussian Random Fields"
                    :items="$store.state.options.colorScale.legal"
                  />
                </v-col>
                <v-col
                  md="6"
                >
                  <v-select
                    v-model="faciesColorLibrary"
                    label="The color library for Facies"
                    :items="$store.getters['constants/faciesColors/libraries']"
                  >
                    <template #item="{ item }">
                      <v-col
                        align-self="space-between"
                      >
                        <v-row>
                          <v-col cols="12">
                            {{ item.text }}
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
        <br>
        <grid-information
          :grid-size="gridSize"
          :simulation-settings="simulationSettings"
        />
      </v-card-text>
      <v-card-actions>
        {{ version && `Version: ${version}` }}
        <v-spacer />
        <bold-button
          title="Cancel"
          @click="cancel"
        />
        <bold-button
          title="Ok"
          :disabled="hasErrors"
          :tooltip-text="hasErrors && 'Some value(s) are invalid'"
          @click="ok"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'
import rms from '@/api/rms'
import LoggingSettings from '@/components/dialogs/JobSettings/LoggingSettings.vue'
import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'
import BoldButton from '@/components/baseComponents/BoldButton.vue'
import NumericField from '@/components/selection/NumericField.vue'
import FmuSettings from '@/components/dialogs/JobSettings/FmuSettings.vue'
import RunSettings from '@/components/dialogs/JobSettings/RunSettings.vue'
import GridInformation from '@/components/dialogs/JobSettings/GridInformation.vue'
import TransformtypeSettings from '@/components/dialogs/JobSettings/TransformtypeSettings.vue'

import ColorLibrary from '@/utils/domain/colorLibrary'
import { Optional } from '@/utils/typing'
import { Store } from '@/store/typing'
import { Coordinate3D, SimulationSettings } from '@/utils/domain/bases/interfaces'

interface Invalid {
  fmu: boolean
}

@Component({
  components: {
    RunSettings,
    LoggingSettings,
    SettingsPanel,
    FmuSettings,
    NumericField,
    BoldButton,
    GridInformation,
    TransformtypeSettings,
  },
})
export default class JobSettings extends Vue {
  invalid: Invalid = {
    fmu: false,
  }

  dialog = false
  showZoneNameNumber = ''
  showRegionNameNumber = ''
  automaticAlphaFieldSelection = false
  automaticFaciesFill = false
  automaticObservedFaciesSelection = false
  filterZeroProbability = false
  runFmuWorkflows = false
  colorScale = ''
  faciesColorLibrary: Optional<ColorLibrary> = null
  maxLayersInFmu: Optional<number> = null
  debugLevel = 0
  transformType = 0
  importFields = false
  fmuGrid = ''
  createFmuGrid = false
  onlyUpdateFromFmu = false
  maxAllowedFractionOfValuesOutsideTolerance = 0
  toleranceOfProbabilityNormalisation = 0
  fieldFileFormat = ''
  customTrendExtrapolationMethod = ''
  exportFmuConfigFiles = false
  onlyUpdateResidualFields = false

  get simulationSettings (): SimulationSettings { return this.$store.getters.simulationSettings() }
  get gridSize (): Coordinate3D { return this.simulationSettings.gridSize }
  get version (): string { return process.env.VUE_APP_APS_VERSION || '' }
  get currentGridModel (): string { return this.$store.getters.gridModel }


  @Watch('dialog')
  onActivation (value: boolean): void {
    if (value) {
      const options = (this.$store as Store).state.options
      const parameters = this.$store.state.parameters
      const fmu = this.$store.state.fmu

      this.maxLayersInFmu = fmu.maxDepth.value
      this.runFmuWorkflows = fmu.runFmuWorkflows.value
      this.onlyUpdateFromFmu = fmu.onlyUpdateFromFmu.value
      this.fmuGrid = fmu.simulationGrid.current
      this.createFmuGrid = fmu.create.value
      this.fieldFileFormat = fmu.fieldFileFormat.value
      this.customTrendExtrapolationMethod = fmu.customTrendExtrapolationMethod.value
      this.onlyUpdateResidualFields = fmu.onlyUpdateResidualFields.value

      this.debugLevel = parameters.debugLevel.selected
      this.transformType = parameters.transformType.selected
      this.maxAllowedFractionOfValuesOutsideTolerance = parameters.maxAllowedFractionOfValuesOutsideTolerance.selected
      this.toleranceOfProbabilityNormalisation = parameters.toleranceOfProbabilityNormalisation.selected
      this.showZoneNameNumber = options.showNameOrNumber.zone.value
      this.showRegionNameNumber = options.showNameOrNumber.region.value
      this.automaticAlphaFieldSelection = options.automaticAlphaFieldSelection.value
      this.automaticObservedFaciesSelection = options.automaticObservedFaciesSelection.value
      this.automaticFaciesFill = options.automaticFaciesFill.value
      this.filterZeroProbability = options.filterZeroProbability.value
      this.importFields = options.importFields.value
      this.exportFmuConfigFiles = options.exportFmuConfigFiles.value
      this.colorScale = options.colorScale.value
      this.faciesColorLibrary = this.$store.getters['constants/faciesColors/current']
    }
  }

  cancel (): void {
    this.dialog = false
  }

  async ok (): Promise<void> {
    const dispatch = this.$store.dispatch
    await Promise.all([
      dispatch('parameters/debugLevel/select', this.debugLevel),
      dispatch('parameters/transformType/select', this.transformType),
      dispatch('parameters/maxAllowedFractionOfValuesOutsideTolerance/select', this.maxAllowedFractionOfValuesOutsideTolerance),
      dispatch('parameters/toleranceOfProbabilityNormalisation/select', this.toleranceOfProbabilityNormalisation),
      dispatch('fmu/maxDepth/set', this.maxLayersInFmu),
      dispatch('fmu/runFmuWorkflows/set', this.runFmuWorkflows),
      dispatch('fmu/onlyUpdateFromFmu/set', this.onlyUpdateFromFmu),
      dispatch('fmu/simulationGrid/set', this.fmuGrid),
      dispatch('fmu/create/set', this.createFmuGrid),
      dispatch('fmu/fieldFileFormat/set', this.fieldFileFormat),
      dispatch('fmu/customTrendExtrapolationMethod/set', this.customTrendExtrapolationMethod),
      dispatch('fmu/onlyUpdateResidualFields/set', this.onlyUpdateResidualFields),

      dispatch('options/showNameOrNumber/zone/set', this.showZoneNameNumber),
      dispatch('options/showNameOrNumber/region/set', this.showRegionNameNumber),
      dispatch('options/automaticAlphaFieldSelection/set', this.automaticAlphaFieldSelection),
      dispatch('options/automaticObservedFaciesSelection/set', this.automaticObservedFaciesSelection),
      dispatch('options/automaticFaciesFill/set', this.automaticFaciesFill),
      dispatch('options/filterZeroProbability/set', this.filterZeroProbability),
      dispatch('options/importFields/set', this.importFields),
      dispatch('options/exportFmuConfigFiles/set', this.exportFmuConfigFiles),
      dispatch('options/colorScale/set', this.colorScale),

      dispatch('constants/faciesColors/set', this.faciesColorLibrary),
    ])
    // Create ERTBOX grid if this.createFmuGrid is true
    if (this.createFmuGrid){
      rms.createErtBoxGrid(this.currentGridModel, this.fmuGrid, this.maxLayersInFmu, this.debugLevel)
      this.createFmuGrid = false
      await Promise.all([
        dispatch('fmu/create/set', this.createFmuGrid),
        dispatch('gridModels/refresh')
      ])
    }

    this.dialog = false
  }

  update (type: string, value: boolean): void {
    Vue.set(this.invalid, type, value)
  }

  get hasErrors (): boolean { return Object.values(this.invalid).some(invalid => invalid) }
}

</script>

<style lang="scss" scoped>
input[type=text] {
    border: 2px solid blue;
    border-radius: 4px;
}
</style>

<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="800"
    scrollable
  >
    <template v-slot:activator="{ on }">
      <v-btn
        outlined
        color="primary"
        dark
        v-on="on"
      >
        Project Settings
      </v-btn>
    </template>
    <v-card>
      <v-card-title
        class="headline"
      >
        {{ title }}
      </v-card-title>
      <v-card-text>
        <v-card
          outlined
        >
          <v-list-item>
            <v-list-item-title
              class="headline"
            >
              Folder Settings
            </v-list-item-title>
          </v-list-item>
          <v-row no-gutters>
            <v-col
              class="pa-2"
              cols="3"
            >
              APS Model File Location:
            </v-col>
            <v-col
              class="pa-2"
              cols="5"
            >
              <v-text-field
                v-model="apsModelFileLocation"
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
                @click="chooseApsModelFileLocation"
              />
            </v-col>
          </v-row>
        </v-card>
        <br>
        <FmuSettings
          :fmu-parameter-list-location.sync="fmuParameterListLocation"
          :run-fmu-workflows.sync="runFmuWorkflows"
        />
        <br>
        <v-card
          outlined
        >
          <v-list-item>
            <v-list-item-title
              class="headline"
            >
              Display Settings
            </v-list-item-title>
          </v-list-item>
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
                    <template v-slot:item="{ item }">
                      <v-col
                        align-self="space-between"
                      >
                        {{ item.text }}
                        <v-row>
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
                  label="Automatically assign fields to alpha channels"
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
        </v-card>
        <br>
        <v-card
          v-if="!!$store.getters.gridModel"
          outlined
        >
          <v-list-item>
            <v-list-item-title
              class="headline"
            >
              Grid model
            </v-list-item-title>
          </v-list-item>
          <v-container
            v-if="!$store.getters['parameters/grid/waiting']"
            class="text-center"
          >
            <v-row
              class="fill"
              justify="space-around"
            >
              <v-col cols="4">
                <numeric-field
                  v-model="gridSize.x"
                  discrete
                  unit="cell"
                  label="X"
                  hint="The size of the grid"
                  persistent-hint
                />
              </v-col>
              <v-col cols="4">
                <numeric-field
                  v-model="gridSize.y"
                  discrete
                  unit="cell"
                  label="Y"
                  hint="The size of the grid"
                  persistent-hint
                />
              </v-col>
              <v-col cols="4">
                <numeric-field
                  v-model="gridSize.z"
                  discrete
                  unit="cell"
                  label="Z"
                  hint="The size of the grid"
                  persistent-hint
                />
              </v-col>
              <v-spacer />
              <v-col cols="4">
                <numeric-field
                  :value="simulationSettings.simulationBox.x"
                  label="X"
                  unit="m"
                  hint="The size of the simulation box"
                  persistent-hint
                />
              </v-col>
              <v-col cols="4">
                <numeric-field
                  :value="simulationSettings.simulationBox.y"
                  label="Y"
                  unit="m"
                  hint="The size of the simulation box"
                  persistent-hint
                />
              </v-col>
              <v-col cols="4">
                <numeric-field
                  :value="simulationSettings.simulationBox.z"
                  label="Z"
                  unit="m"
                  hint="The size of the simulation box"
                  persistent-hint
                />
              </v-col>
              <v-col cols="4">
                <numeric-field
                  :value="simulationSettings.gridAzimuth"
                  :ranges="{min: -360, max: 360}"
                  label="Grid azimuth"
                  unit="°"
                  hint="The angle between the grid, and UTM"
                  persistent-hint
                />
              </v-col>
              <v-col cols="4">
                <numeric-field
                  :value="simulationSettings.simulationBoxOrigin.x"
                  label="X"
                  unit="m"
                  hint="Origin of simulation box"
                  persistent-hint
                />
              </v-col>
              <v-col cols="4">
                <numeric-field
                  :value="simulationSettings.simulationBoxOrigin.y"
                  label="Y"
                  unit="m"
                  hint="Origin of simulation box"
                  persistent-hint
                />
              </v-col>
            </v-row>
          </v-container>
          <v-container
            v-else
          >
            <v-row
              justify="center"
              align="center"
            >
              <v-icon
                x-large
                v-text="$vuetify.icons.values.refreshSpinner"
              />
            </v-row>
          </v-container>
        </v-card>
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
          @click="ok"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'

import rms from '@/api/rms'

import BoldButton from '@/components/baseComponents/BoldButton.vue'
import NumericField from '@/components/selection/NumericField.vue'
import FmuSettings from '@/components/dialogs/FmuSettings.vue'

import ColorLibrary from '@/utils/domain/colorLibrary'
import { Optional } from '@/utils/typing'

@Component({
  // @ts-ignore
  asyncComputed: {
    async title () {
      const name = await rms.projectName()
      return name ? `Project settings for ${name}` : 'Project settings'
    },
  },

  components: {
    FmuSettings,
    NumericField,
    BoldButton
  },
})
export default class ProjectSettings extends Vue {
  dialog: boolean = false
  apsModelFileLocation: string = ''
  fmuParameterListLocation: string = ''
  showZoneNameNumber: string = ''
  showRegionNameNumber: string = ''
  automaticAlphaFieldSelection: string = ''
  automaticFaciesFill: string = ''
  filterZeroProbability: boolean = false
  runFmuWorkflows: boolean = false
  colorScale: string = ''
  faciesColorLibrary: Optional<ColorLibrary> = null

  get simulationSettings () { return this.$store.getters.simulationSettings() }
  get gridSize () { return this.simulationSettings.gridSize }
  get version () { return process.env.VUE_APP_APS_VERSION || '' }

  @Watch('dialog')
  onActivation (value: boolean) {
    if (value) {
      const options = this.$store.state.options
      const path = this.$store.state.parameters.path

      this.apsModelFileLocation = path.project.selected
      this.fmuParameterListLocation = path.fmuParameterListLocation.selected
      this.showZoneNameNumber = options.showNameOrNumber.zone.value
      this.showRegionNameNumber = options.showNameOrNumber.region.value
      this.automaticAlphaFieldSelection = options.automaticAlphaFieldSelection.value
      this.automaticFaciesFill = options.automaticFaciesFill.value
      this.filterZeroProbability = options.filterZeroProbability.value
      this.runFmuWorkflows = options.runFmuWorkflows.value
      this.colorScale = options.colorScale.value
      this.faciesColorLibrary = this.$store.getters['constants/faciesColors/current']
    }
  }

  chooseApsModelFileLocation () {
    rms.chooseDir('load').then((path: string): void => {
      if (path) {
        this.apsModelFileLocation = path
      }
    })
  }
  cancel () {
    this.dialog = false
  }
  async ok () {
    const dispatch = this.$store.dispatch
    await Promise.all([
      dispatch('parameters/path/project/select', this.apsModelFileLocation),
      dispatch('parameters/path/fmuParameterListLocation/select', this.fmuParameterListLocation),
      dispatch('options/showNameOrNumber/zone/set', this.showZoneNameNumber),
      dispatch('options/showNameOrNumber/region/set', this.showRegionNameNumber),
      dispatch('options/automaticAlphaFieldSelection/set', this.automaticAlphaFieldSelection),
      dispatch('options/automaticFaciesFill/set', this.automaticFaciesFill),
      dispatch('options/filterZeroProbability/set', this.filterZeroProbability),
      dispatch('options/runFmuWorkflows/set', this.runFmuWorkflows),
      dispatch('options/colorScale/set', this.colorScale),
      dispatch('constants/faciesColors/set', this.faciesColorLibrary),
    ])
    this.dialog = false
  }
}

</script>

<style lang="scss" scoped>
input[type=text] {
    border: 2px solid blue;
    border-radius: 4px;
}
</style>

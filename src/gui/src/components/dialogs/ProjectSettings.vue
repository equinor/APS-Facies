<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="800"
  >
    <v-btn
      slot="activator"
      outline
      color="primary"
      dark
    >
      Project Settings
    </v-btn>
    <v-card>
      <v-card-title
        class="headline"
      >
        {{ title }}
      </v-card-title>
      <v-card-text>
        <fieldset>
          <legend>
            Folder Settings:
          </legend>
          <v-layout
            row
            wrap
          >
            <v-flex
              xs3
              pa-2
            >
              APS Model File Location:
            </v-flex>
            <v-flex
              xs5
              pa-2
            >
              <v-text-field
                v-model="apsModelFileLocation"
                single-line
                solo
              />
            </v-flex>
            <v-flex
              xs4
              pa-2
            >
              <bold-button
                title="Select Directory"
                @click="chooseAPSModelFileLocation"
              />
            </v-flex>

            <v-flex
              xs3
            >
              Truncation Rule File Location:
            </v-flex>
            <v-flex
              xs5
            >
              <v-text-field
                v-model="truncationRuleLocation"
                single-line
                solo
              />
            </v-flex>
            <v-flex
              xs4
            >
              <bold-button
                title="Select Directory"
                @click="chooseTruncationRuleFileLocation"
              />
            </v-flex>

            <v-flex
              xs3
            >
              FMU Parameters List Location:
            </v-flex>
            <v-flex
              xs5
            >
              <v-text-field
                v-model="fmuParameterListLocation"
                single-line
                solo
              />
            </v-flex>
            <v-flex
              xs4
            >
              <bold-button
                title="Select Directory"
                @click="chooseFMUparametersFileLocation"
              />
            </v-flex>
          </v-layout>
        </fieldset>
        <br>
        <fieldset>
          <legend>
            Display Settings:
          </legend>
          <v-layout>
            <v-flex
              pa-2
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
            </v-flex>
            <v-flex
              pa-2
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
            </v-flex>
            <v-layout column>
              <v-flex>
                <v-checkbox
                  v-model="automaticAlphaFieldSelection"
                  label="Automatically assign fields to alpha channels"
                />
              </v-flex>
              <v-flex>
                <v-checkbox
                  v-model="automaticFaciesFill"
                  label="Automatically assign facies to templates"
                />
              </v-flex>
              <v-flex>
                <v-checkbox
                  v-model="filterZeroProbability"
                  label="Ignore Facies with 0 probability"
                />
              </v-flex>
            </v-layout>
          </v-layout>
        </fieldset>
        <fieldset
          v-if="!!$store.getters.gridModel"
        >
          <legend>Grid model</legend>
          <v-container
            v-if="!$store.getters['simulationSettings/waiting']"
            grid-list-md
            text-xs-center
          >
            <v-layout
              justify-space-around
              align-space-around
              row
              fill
              wrap
            >
              <v-flex xs4>
                <numeric-field
                  v-model="gridSize.x"
                  discrete
                  unit="cell"
                  label="X"
                  hint="The size of the grid"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  v-model="gridSize.y"
                  discrete
                  unit="cell"
                  label="Y"
                  hint="The size of the grid"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  v-model="gridSize.z"
                  discrete
                  unit="cell"
                  label="Z"
                  hint="The size of the grid"
                  persistent-hint
                />
              </v-flex>
              <v-spacer />
              <v-flex xs4>
                <numeric-field
                  :value="simulationSettings.simulationBox.x"
                  label="X"
                  unit="m"
                  hint="The size of the simulation box"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  :value="simulationSettings.simulationBox.y"
                  label="Y"
                  unit="m"
                  hint="The size of the simulation box"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  :value="simulationSettings.simulationBox.z"
                  label="Z"
                  unit="m"
                  hint="The size of the simulation box"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  :value="simulationSettings.gridAzimuth"
                  :ranges="{min: -360, max: 360}"
                  label="Grid azimuth"
                  unit="°"
                  hint="The angle between the grid, and UTM"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  :value="simulationSettings.simulationBoxOrigin.x"
                  label="X"
                  unit="m"
                  hint="Origin of simulation box"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  :value="simulationSettings.simulationBoxOrigin.y"
                  label="Y"
                  unit="m"
                  hint="Origin of simulation box"
                  persistent-hint
                />
              </v-flex>
            </v-layout>
          </v-container>
          <v-layout
            v-else
            justify-center
          >
            <v-icon
              x-large
              v-text="$vuetify.icons.refreshSpinner"
            />
          </v-layout>
        </fieldset>
      </v-card-text>
      <v-card-actions>
        Version: {{ version }}
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

@Component({
  // @ts-ignore
  asyncComputed: {
    async title () {
      const name = await rms.projectName()
      return name ? `Project settings for ${name}` : 'Project settings'
    },
  },

  components: {
    NumericField,
    BoldButton
  },
})
export default class ProjectSettings extends Vue {
  dialog: boolean = false
  apsModelFileLocation: string = ''
  truncationRuleLocation: string = ''
  fmuParameterListLocation: string = ''
  showZoneNameNumber: string = ''
  showRegionNameNumber: string = ''
  automaticAlphaFieldSelection: string = ''
  automaticFaciesFill: string = ''
  filterZeroProbability: boolean = false

  get simulationSettings () { return this.$store.getters.simulationSettings() }
  get gridSize () { return this.simulationSettings.gridSize }
  get version () { return process.env.VUE_APP_APS_VERSION || '' }

  @Watch('dialog')
  onActivation (value: boolean) {
    if (value) {
      this.apsModelFileLocation = this.$store.state.parameters.path.project.selected
      this.showZoneNameNumber = this.$store.state.options.showNameOrNumber.zone.value
      this.showRegionNameNumber = this.$store.state.options.showNameOrNumber.region.value
      this.automaticAlphaFieldSelection = this.$store.state.options.automaticAlphaFieldSelection.value
      this.automaticFaciesFill = this.$store.state.options.automaticFaciesFill.value
      this.filterZeroProbability = this.$store.state.options.filterZeroProbability.value
    }
  }

  chooseAPSModelFileLocation () {
    rms.chooseDir('load').then((path: string): void => {
      if (path) {
        this.apsModelFileLocation = path
      }
    })
  }
  chooseTruncationRuleFileLocation () {
    rms.chooseDir('load').then((path: string): void => {
      if (path) {
        this.truncationRuleLocation = path
      }
    })
  }
  chooseFMUparametersFileLocation () {
    rms.chooseDir('load').then((path: string): void => {
      if (path) {
        this.fmuParameterListLocation = path
      }
    })
  }
  cancel () {
    this.dialog = false
  }
  async ok () {
    alert(`dialogTruncationRuleLocation:   ${this.truncationRuleLocation}
          dialogFMUParameterListLocation: ${this.fmuParameterListLocation}`)
    await Promise.all([
      this.$store.dispatch('parameters/path/project/select', this.apsModelFileLocation),
      this.$store.dispatch('options/showNameOrNumber/zone/set', this.showZoneNameNumber),
      this.$store.dispatch('options/showNameOrNumber/region/set', this.showRegionNameNumber),
      this.$store.dispatch('options/automaticAlphaFieldSelection/set', this.automaticAlphaFieldSelection),
      this.$store.dispatch('options/automaticFaciesFill/set', this.automaticFaciesFill),
      this.$store.dispatch('options/filterZeroProbability/set', this.automaticAlphaFieldSelection),
    ])
    this.dialog = false
  }
}

</script>

<style scoped>
input[type=text] {
    border: 2px solid blue;
    border-radius: 4px;
}
</style>

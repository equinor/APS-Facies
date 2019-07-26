<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="500px"
    @keydown.esc="cancel"
  >
    <v-card>
      <v-card-title>
        <span class="headline">
          Visualization settings
        </span>
      </v-card-title>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-layout>
              <!--Seed-->
              <v-flex xs10>
                <numeric-field
                  v-model="settings.seed"
                  :ranges="{min: 0, max: Math.pow(2, 64) - 1}"
                  label="Seed"
                />
              </v-flex>
              <v-flex
                xs2
              >
                <icon-button
                  icon="random"
                  @click="settings.seed = newSeed()"
                />
              </v-flex>
            </v-layout>
            <v-flex xs6>
              <v-checkbox
                :value="settings.gridModel.use"
                label="Use model grid"
                @change="val => settings.gridModel.use = val"
              />
            </v-flex>
            <v-flex xs6 />
            <v-layout
              v-if="settings.gridModel.use"
              justify-space-around
              wrap
            >
              <v-flex xs4>
                <numeric-field
                  v-model="settings.gridModel.size.x"
                  discrete
                  unit="cell"
                  label="X"
                  hint="The size of the grid to be simulated"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  v-model="settings.gridModel.size.y"
                  discrete
                  unit="cell"
                  label="Y"
                  hint="The size of the grid to be simulated"
                  persistent-hint
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  v-model="settings.gridModel.size.z"
                  discrete
                  unit="cell"
                  label="Z"
                  hint="The size of the grid to be simulated"
                  persistent-hint
                />
              </v-flex>
            </v-layout>
          </v-layout>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="blue darken-1"
          text
          @click="cancel"
        >
          Close
        </v-btn>
        <v-btn
          color="blue darken-1"
          text
          @click="save"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import APSError from '@/utils/domain/errors/base'

import { DialogOptions } from '@/utils/domain/bases/interfaces'
import { Optional } from '@/utils/typing'
import { Color } from '@/utils/domain/facies/helpers/colors'

import NumericField from '@/components/selection/NumericField.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { newSeed } from '@/utils'

interface Settings {
  crossSection: {
    type: Optional<'IJ' | 'IK' | 'JK'>
    relativePosition: Optional<number>
  }
  gridModel: {
    use: boolean
    size: {
      x: number
      y: number
      z: number
    }
  }
  seed: Optional<number>
}

interface ReturnValue {
  save: boolean
  settings: Settings | {}
}

@Component({
  components: {
    IconButton,
    NumericField,
  },
})
export default class VisualizationSettingsDialog extends Vue {
  dialog: boolean = false
  resolve: Optional<({ save, settings }: ReturnValue) => void> = null
  reject: Optional<({ save, settings }: ReturnValue) => void> = null
  settings: Settings = {
    crossSection: {
      type: null,
      relativePosition: null,
    },
    gridModel: {
      use: false,
      size: {
        x: 100, y: 100, z: 1,
      },
    },
    seed: null,
  }
  options: DialogOptions = {
    color: (this.$vuetify.theme.themes.light.primary as Color),
    width: 290,
  }

  open (settings: Settings, options: DialogOptions = {}) {
    this.dialog = true
    this.settings = settings
    this.options = Object.assign(this.options, options)
    return new Promise((resolve, reject) => {
      this.resolve = resolve
      this.reject = reject
    })
  }
  save () {
    if (!this.resolve) throw new APSError('The `resolve` callback has not been set')
    this.resolve({ save: true, settings: this.settings })
    this.dialog = false
  }
  cancel () {
    if (!this.resolve) throw new APSError('The `resolve` callback has not been set')
    this.resolve({ save: false, settings: {} })
    this.dialog = false
  }
  newSeed () {
    return newSeed()
  }
}
</script>

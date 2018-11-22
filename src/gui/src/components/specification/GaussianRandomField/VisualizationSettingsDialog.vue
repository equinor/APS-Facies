<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="500px"
    @keydown.esc="cancel"
  >
    <v-card>
      <v-card-title>
        <span class="headline">Visualization settings</span>
      </v-card-title>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            <!--Cross section-->
            <v-flex
              xs12
              sm6
              md6
            >
              <v-select
                v-model="settings.crossSection.type"
                :items="['IJ', 'IK', 'JK']"
                label="Cross section type"
                required
              />
            </v-flex>
            <v-flex
              xs12
              sm6
              md6
            >
              <fraction-field
                v-model="settings.crossSection.relativePosition"
                label="Relative position"
              />
            </v-flex>
            <v-layout row>
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
                :value="!settings.gridModel.use"
                label="Use model grid"
                @change="val => settings.gridModel.use = !val"
              />
            </v-flex>
            <v-flex xs6/>
            <v-layout
              v-if="settings.gridModel.use"
              justify-space-around
              row
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
        <v-spacer/>
        <v-btn
          color="blue darken-1"
          flat
          @click="cancel">Close</v-btn>
        <v-btn
          color="blue darken-1"
          flat
          @click="save">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import NumericField from '@/components/selection/NumericField'
import FractionField from '@/components/selection/FractionField'
import IconButton from '@/components/selection/IconButton'

import { newSeed } from '@/utils'

export default {
  components: {
    IconButton,
    FractionField,
    NumericField,
  },

  data () {
    return {
      dialog: false,
      resolve: null,
      reject: null,
      settings: {
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
      },
      options: {
        color: 'primary',
        width: 290,
      }
    }
  },

  methods: {
    open (settings, options) {
      this.dialog = true
      this.settings = settings
      this.options = Object.assign(this.options, options)
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    save () {
      this.resolve({ save: true, settings: this.settings })
      this.dialog = false
    },
    cancel () {
      this.resolve({ save: false, settings: {} })
      this.dialog = false
    },
    newSeed () {
      return newSeed()
    },
  },
}
</script>

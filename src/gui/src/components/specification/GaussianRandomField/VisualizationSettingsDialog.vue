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
              <numeric-field
                v-model="settings.crossSection.relativePosition"
                :ranges="{min: 0, max: 1}"
                label="Relative position"
              />
            </v-flex>
            <v-layout row>
              <!--Grid azimuth angle-->
              <v-flex xs6>
                <numeric-field
                  v-model="settings.gridAzimuth"
                  :ranges="{min: 0, max: 360}"
                  label="Grid azimuth"
                />
              </v-flex>
              <!--Seed-->
              <v-layout row>
                <v-flex>
                  <numeric-field
                    v-model="settings.seed.value"
                    :disabled="settings.seed.autoRenew"
                    :ranges="{min: 0, max: Math.pow(2, 64) - 1}"
                    label="Seed"
                  />
                </v-flex>
                <v-flex xs2>
                  <v-checkbox
                    v-model="settings.seed.autoRenew"
                  />
                </v-flex>
                <v-flex
                  v-if="settings.seed.autoRenew"
                  xs2
                >
                  <v-btn
                    icon
                    @click="settings.seed.value = newSeed()"
                  >
                    <v-icon>refresh</v-icon>
                  </v-btn>
                </v-flex>
              </v-layout>
            </v-layout>
            <!--Grid size-->
            Grid size
            <v-layout row>
              <v-flex xs4>
                <numeric-field
                  v-model="settings.gridSize.x"
                  label="X"
                  discrete
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  v-model="settings.gridSize.y"
                  label="Y"
                  discrete
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  v-model="settings.gridSize.z"
                  label="Z"
                  discrete
                />
              </v-flex>
            </v-layout>
            <!--Simulation box size-->
            Simulation box size
            <v-layout row>
              <v-flex xs4>
                <numeric-field
                  v-model="settings.simulationBox.x"
                  label="X"
                  discrete
                  unit="m"
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  v-model="settings.simulationBox.y"
                  label="Y"
                  discrete
                  unit="m"
                />
              </v-flex>
              <v-flex xs4>
                <numeric-field
                  v-model="settings.simulationBox.z"
                  label="Z"
                  discrete
                  unit="m"
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
import { newSeed } from '@/utils'

export default {
  components: {
    NumericField,
  },

  data () {
    return {
      dialog: false,
      resolve: null,
      reject: null,
      grfId: null,
      settings: {
        crossSection: {
          type: null,
          relativePosition: null,
        },
        gridAzimuth: null,
        gridSize: {
          x: null, y: null, z: null,
        },
        simulationBox: {
          x: null, y: null, z: null,
        },
        seed: {value: null, autoRenew: true},
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
      // this.grfId = grfId
      this.settings = settings
      // this.setSettings()
      this.options = Object.assign(this.options, options)
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    save () {
      this.resolve({save: true, settings: this.settings})
      this.dialog = false
    },
    cancel () {
      this.resolve({save: false, settings: {}})
      this.dialog = false
    },
    newSeed () {
      return newSeed()
    }
  },
}
</script>

<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="800"
  >
    <v-btn
      slot="activator"
      color="primary"
      dark
    >
      Project Settings
    </v-btn>
    <v-card>
      <v-card-title
        class="headline"
      >
        Project Settings
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
            <v-flex>
              <v-checkbox
                v-model="automaticAlphaFieldSelection"
                label="Automatically assign fields to alpha channels"
              />
            </v-flex>
          </v-layout>
        </fieldset>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
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

<script>

import BoldButton from '@/components/baseComponents/BoldButton'

export default {

  components: {
    BoldButton
  },

  data () {
    return {
      dialog: false,
      apsModelFileLocation: '',
      truncationRuleLocation: '',
      fmuParameterListLocation: '',
      showZoneNameNumber: '',
      showRegionNameNumber: '',
      automaticAlphaFieldSelection: ''
    }
  },

  watch: {
    dialog: function (value) {
      if (value) {
        this.showZoneNameNumber = this.$store.state.options.showNameOrNumber.zone.value
        this.showRegionNameNumber = this.$store.state.options.showNameOrNumber.region.value
        this.automaticAlphaFieldSelection = this.$store.state.options.automaticAlphaFieldSelection.value
      }
    },
  },

  methods: {
    chooseAPSModelFileLocation (e) {
      // eslint-disable-next-line no-undef
      rms.chooseDir('load').then(path => {
        if (path) {
          this.apsModelFileLocation = path
        }
      })
    },
    chooseTruncationRuleFileLocation (e) {
      // eslint-disable-next-line no-undef
      rms.chooseDir('load').then(path => {
        if (path) {
          this.truncationRuleLocation = path
        }
      })
    },
    chooseFMUparametersFileLocation (e) {
      // eslint-disable-next-line no-undef
      rms.chooseDir('load').then(path => {
        if (path) {
          this.fmuParameterListLocation = path
        }
      })
    },
    cancel (e) {
      this.dialog = false
    },
    ok (e) {
      // TODO: Store stuff
      alert(`dialogAPSModelFileLocation:    ${this.apsModelFileLocation}
            dialogTruncationRuleLocation:   ${this.truncationRuleLocation}
            dialogFMUParameterListLocation: ${this.fmuParameterListLocation}
            dialogShowZoneNameNumber:       ${this.showZoneNameNumber}
            dialogShowRegionNameNumber:     ${this.showRegionNameNumber}`)
      this.$store.dispatch('options/showNameOrNumber/zone/set', this.showZoneNameNumber)
      this.$store.dispatch('options/showNameOrNumber/region/set', this.showRegionNameNumber)
      this.$store.dispatch('options/automaticAlphaFieldSelection/set', this.automaticAlphaFieldSelection)
      this.dialog = false
    }
  },
}

</script>

<style scoped>
input[type=text] {
    border: 2px solid blue;
    border-radius: 4px;
}
</style>

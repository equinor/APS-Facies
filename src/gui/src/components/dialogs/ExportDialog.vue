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
          save export dialog.
        </span>
      </v-card-title>
      <v-card-text>
        <fieldset>
          <legend>
            Select File to save to:
          </legend>
          <v-layout
            row
            wrap
          >
            <v-flex
              xs5
              pa-2
            >
              <v-text-field
                v-model="path"
                single-line
                solo
              />
            </v-flex>
            <v-flex
              xs4
              pa-2
            >
              <bold-button
                title="Select File"
                @click="chooseAPSModelFile"
              />
            </v-flex>
          </v-layout>
        </fieldset>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="blue darken-1"
          flat
          @click="choose"
        >
          Save
        </v-btn>
        <v-btn
          color="blue darken-1"
          flat
          @click="abort"
        >
          Abort
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import BoldButton from '@/components/baseComponents/BoldButton'
import rms from '@/api/rms'

export default {
  components: {
    BoldButton
  },
  data () {
    return {
      dialog: false,
      resolve: null,
      reject: null,
      path: null
    }
  },
  methods: {
    chooseAPSModelFile () {
      // eslint-disable-next-line no-undef
      rms.chooseFile('save', '', '').then(result => { // setting parameters filter and suggestion does not seem to work...
        if (result) {
          this.path = result
        }
      })
    },
    open (defaultPath) {
      this.dialog = true
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
        this.path = defaultPath
      })
    },
    choose () {
      this.resolve({ save: true, path: this.path })
      this.dialog = false
    },
    abort () {
      this.resolve({ save: false })
      this.dialog = false
    }
  }
}
</script>

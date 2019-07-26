<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="500px"
    @keydown.esc="abort"
    @keydown.enter="choose"
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
            Select File to save to
          </legend>
          <v-layout
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
          text
          @click="choose"
        >
          Save
        </v-btn>
        <v-btn
          color="blue darken-1"
          text
          @click="abort"
        >
          Abort
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import BoldButton from '@/components/baseComponents/BoldButton.vue'

import { APSError } from '@/utils/domain/errors'
import rms from '@/api/rms'

@Component({
  components: {
    BoldButton,
  },
})
export default class ExportDialog extends Vue {
  dialog: boolean = false
  resolve: ((value: { save: boolean, path: string }) => void) | null = null
  reject: ((reason: string) => void) | null = null
  path: string | null = null

  chooseAPSModelFile () {
    rms.chooseFile('save', '', '').then((result: string | null): void => { // setting parameters filter and suggestion does not seem to work...
      if (result) {
        this.path = result
      }
    })
  }

  open (defaultPath: string): Promise<{save: boolean, path: string }> {
    this.dialog = true
    this.path = defaultPath
    return new Promise((resolve, reject) => {
      this.resolve = resolve
      this.reject = reject
    })
  }

  choose () {
    if (!this.resolve) throw new APSError('resolve has not been set')
    if (!this.path) throw new APSError('path has not been set')

    this.resolve({ save: true, path: this.path })
    this.dialog = false
  }

  abort () {
    if (!this.resolve) throw new APSError('resolve has not been set')

    this.resolve({ save: false, path: '' })
    this.dialog = false
  }
}
</script>

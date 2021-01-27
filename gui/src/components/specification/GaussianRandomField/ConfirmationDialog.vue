<template>
  <v-dialog
    v-model="dialog"
    :max-width="options.width"
    @keydown.esc="cancel()"
    @keydown.enter="agree()"
  >
    <v-toolbar
      :color="options.color"
      dark
      dense
    >
      <v-toolbar-title class="white--text">
        {{ title }}
      </v-toolbar-title>
    </v-toolbar>
    <v-card tile>
      <v-card-text v-show="!!message">
        {{ message }}
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="warning darken-1"
          text
          @click.native="agree()"
        >
          Yes
        </v-btn>
        <v-btn
          color="grey"
          text
          @click.native="cancel()"
        >
          Cancel
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
/**
 * Vuetify Confirm Dialog component
 * Borrowed from: https://gist.github.com/eolant/ba0f8a5c9135d1a146e1db575276177d
 *
 * Insert component where you want to use it:
 * <confirm ref="confirm"></confirm>
 *
 * Call it:
 * this.$refs.confirm.open('Delete', 'Are you sure?', { color: 'red' }).then((confirm) => {});
 *
 * Alternatively you can place it in main App component and access it globally via this.$root.$confirm
 * <template>
 *   <v-app>
 *     ...
 *     <confirm ref="confirm"></confirm>
 *   </v-app>
 * </template>
 *
 * mounted() {
 *   this.$root.$confirm = this.$refs.confirm.open;
 * }
 */
import { Component, Vue } from 'vue-property-decorator'

import { APSError } from '@/utils/domain/errors'
import { DialogOptions } from '@/utils/domain/bases/interfaces'
import { Color } from '@/utils/domain/facies/helpers/colors'

@Component
export default class ConfirmationDialog extends Vue {
  dialog = false
  resolve: ((answer: boolean) => void) | null = null
  reject: ((answer: boolean) => void) | null = null
  message: string | null = null
  title: string | null = null
  options: DialogOptions = {
    color: (this.$vuetify.theme.themes.light.warning as Color),
    width: 290,
  }

  open (title: string, message: string, options: DialogOptions = {}): Promise<boolean> {
    this.dialog = true
    this.title = title
    this.message = message
    this.options = Object.assign(this.options, options)
    return new Promise((resolve: (answer: boolean) => void, reject: (answer: boolean) => void) => {
      this.resolve = resolve
      this.reject = reject
    })
  }

  agree (): void {
    if (!this.resolve) throw new APSError('resolve has not been set')

    this.resolve(true)
    this.dialog = false
  }

  cancel (): void {
    if (!this.resolve) throw new APSError('resolve has not been set')

    this.resolve(false)
    this.dialog = false
  }
}
</script>

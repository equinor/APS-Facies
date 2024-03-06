<template>
  <v-dialog
    v-model="dialog"
    :max-width="options.width"
    @keydown.esc="cancel()"
    @keydown.enter="agree()"
  >
    <v-toolbar :color="options.color" dark dense>
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
        <v-btn color="warning darken-1" variant="text" @click.native="agree()">
          Yes
        </v-btn>
        <v-btn color="grey" variant="text" @click.native="cancel()">
          Cancel
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
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

import { APSError } from '@/utils/domain/errors'
import type { DialogOptions } from '@/utils/domain/bases/interfaces'
import type { Color } from '@/utils/domain/facies/helpers/colors'
import { ref } from 'vue'
import { useTheme } from 'vuetify'

const dialog = ref(false)
const resolve = ref<((answer: boolean) => void) | null>(null)
const reject = ref<((answer: boolean) => void) | null>(null)
const message = ref<string | null>(null)
const title = ref<string | null>(null)

const theme = useTheme()
const options = ref<DialogOptions>({
  color: theme.global.current.value.colors.warning as Color,
  width: 290,
})

function open(
  newTitle: string,
  newMessage: string,
  newOptions: DialogOptions = {},
): Promise<boolean> {
  dialog.value = true
  title.value = newTitle
  message.value = newMessage
  options.value = { ...options.value, ...newOptions }
  return new Promise(
    (res: (answer: boolean) => void, rej: (answer: boolean) => void) => {
      resolve.value = res
      reject.value = rej
    },
  )
}
defineExpose({ open })

function agree(): void {
  if (!resolve.value) throw new APSError('resolve has not been set')

  resolve.value(true)
  dialog.value = false
}

function cancel(): void {
  if (!resolve.value) throw new APSError('resolve has not been set')

  resolve.value(false)
  dialog.value = false
}
</script>

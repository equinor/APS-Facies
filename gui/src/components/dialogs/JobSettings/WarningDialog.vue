<template>
  <v-dialog
    v-model="isOpen"
    :max-width="options.width"
    @keydown.esc="close()"
    @keydown.enter="close()"
  >
    <v-toolbar :color="options.color" dark dense>
      <v-toolbar-title class="white--text">
        {{ title }}
      </v-toolbar-title>
    </v-toolbar>
    <v-card tile>
      <v-card-text v-if="html" v-show="!!message" v-html="message" />
      <v-card-text v-else v-show="!!message" v-text="message" />
      <v-card-actions>
        <v-spacer />
        <v-btn color="gray" variant="text" @click.native="close()"> OK </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { DialogOptions } from '@/utils/domain/bases/interfaces'
import { Color } from '@/utils/domain/facies/helpers/colors'
import { ref } from 'vue'
import { useTheme } from 'vuetify'

withDefaults(defineProps<{ html?: boolean }>(), { html: false })
const theme = useTheme()
const isOpen = ref<boolean>(false)
const message = ref<string | null>(null)
const title = ref<string | null>(null)
const options = ref<DialogOptions>({
  color: theme.global.current.value.colors.warning as Color,
  width: 290,
})

function close() {
  isOpen.value = false
}

function open(
  newTitle: string,
  newMessage: string,
  newOptions: DialogOptions = {},
) {
  isOpen.value = true
  title.value = newTitle
  message.value = newMessage
  options.value = { ...options, ...newOptions }
}
defineExpose({ open })
</script>

<template>
  <div id="information-bar" v-if="shown">
    <v-alert
      :value="shown"
      :type="type"
      closable
      transition="slide-y-transition"
      @input="shown = false"
    >
      {{ message }}
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { isDevelopmentBuild } from '@/config'
import { delay } from 'lodash'
import type { MessageType } from '@/utils/domain/messages/base'
import type { Optional } from '@/utils/typing'
import { computed, ref, watch } from 'vue'
import { useMessageStore } from '@/stores/messages'

const messageStore = useMessageStore()
const shown = ref(false)

type Message = {
  value: string | Error | null
  readonly kind: MessageType
}
const _message = computed<Message>(
  () => messageStore.message ?? { value: null, kind: 'info' },
)

const message = computed<Optional<string>>(() => {
  let text = _message.value.value
  if (text === null) return text

  if (text instanceof Error) {
    if (isDevelopmentBuild()) {
      throw message
    } else {
      text = text.message
    }
  }
  return text.trim()
})

const type = computed<MessageType>(() => _message.value.kind)

watch(
  _message,
  (message: { value: string | Error | null; kind: MessageType }) => {
    if (message.value) {
      shown.value = true
      const { use, wait } = messageStore.autoDismiss
      if (use) {
        delay(() => (shown.value = false), wait)
      }
    }
  },
)
</script>

<style lang="scss" scoped>
#information-bar {
  .v-alert {
    margin: 0 auto;
    border-width: 0 0 0;
    white-space: pre-line;
    line-height: 1;
  }
}
</style>

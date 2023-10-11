<template>
  <div id="information-bar">
    <v-alert
      :value="shown"
      :type="type"
      dismissible
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
import BaseMessage, { MessageType } from '@/utils/domain/messages/base'
import { Optional } from '@/utils/typing'
import { computed } from 'vue'
import { ref } from 'vue'
import { useStore } from '../store'
import { watch } from 'vue'

const store = useStore()
const shown = ref(false)

const _message = computed<{ value: string | Error | null; kind: MessageType }>(
  () => store.state.message.value ?? { value: null, kind: 'info' },
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

// TODO: Not sure what is wrong with the typing here.
watch(_message, (message: BaseMessage) => {
  if (message.value) {
    shown.value = true
    const { use, wait } = store.state.message.autoDismiss
    if (use) {
      delay(() => (shown.value = false), wait)
    }
  }
})
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

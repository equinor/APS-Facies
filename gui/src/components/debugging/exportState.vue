<template>
  <floating-tooltip trigger="hover">
    <icon-button :icon="clipboardIcon" @click="save" />
    <template #popper> Copy the state to the clipboard </template>
  </floating-tooltip>
</template>

<script setup lang="ts">
import rms from '@/api/rms'

import IconButton from '@/components/selection/IconButton.vue'

import { dumpState } from '@/utils/helpers/processing/export'
import { ref, computed } from 'vue'

type Option = 'may' | 'success' | 'failure'

const status = ref<Option>('may')

const clipboardIcon = computed(() => {
  return {
    may: 'clipboard',
    failure: 'clipboardFailed',
    success: 'clipboardSuccess',
  }[status.value]
})

async function save(): Promise<void> {
  const state = JSON.stringify(dumpState())
  try {
    await navigator.clipboard.writeText(state)
    status.value = 'success'
  } catch (e) {
    status.value = 'failure'
    await rms.save('./state.json', btoa(state), false)
    throw new DOMException(String(e))
  } finally {
    setTimeout(() => {
      status.value = 'may'
    }, 2000)
  }
}
</script>

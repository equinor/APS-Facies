<template>
  <wait-button
    :waiting="executing"
    variant="elevated"
    @click="execute"
  >
    RUN
  </wait-button>
</template>

<script setup lang="ts">
import rms from '@/api/rms'
import { dumpState } from '@/utils/helpers/processing/export'

import WaitButton from '@/components/baseComponents/WaitButton.vue'
import { ref } from 'vue'

const executing = ref(false)

async function execute(): Promise<void> {
  executing.value = true
  const state = JSON.stringify(dumpState())
  await rms.runAPSWorkflow(btoa(state)).finally(() => {
    executing.value = false
  })
}
</script>

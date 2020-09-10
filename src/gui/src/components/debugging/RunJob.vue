<template>
  <wait-button
    :waiting="executing"
    @click="execute"
  >
    RUN
  </wait-button>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import rms from '@/api/rms'
import { dumpState } from '@/utils/helpers/processing/export'

import WaitButton from '@/components/baseComponents/WaitButton.vue'

@Component({
  components: {
    WaitButton,
  }
})
export default class RunJob extends Vue {
  executing = false

  async execute (): Promise<void> {
    this.executing = true
    const state = JSON.stringify(dumpState(this.$store))
    await rms.runAPSWorkflow(btoa(state))
      .finally(() => {
        this.executing = false
      })
  }
}
</script>

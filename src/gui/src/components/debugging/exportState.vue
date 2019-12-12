<template>
  <v-popover
    trigger="hover"
  >
    <icon-button
      :icon="clipboardIcon"
      @click="save"
    />
    <span slot="popover">
      Copy the state to the clipboard
    </span>
  </v-popover>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import rms from '@/api/rms'

import IconButton from '@/components/selection/IconButton.vue'

import { dumpState } from '@/utils/helpers/processing/export'

type Option = 'may' | 'success' | 'failure'

@Component({
  components: {
    IconButton,
  },
})
export default class ExportState extends Vue {
  status: Option = 'may'

  get clipboardIcon () {
    return {
      'may': 'clipboard',
      'failure': 'clipboardFailed',
      'success': 'clipboardSuccess',
    }[this.status]
  }

  async save () {
    const state = JSON.stringify(dumpState(this.$store))
    try {
      await navigator.clipboard.writeText(state)
      this.status = 'success'
    } catch (e) {
      this.status = 'failure'
      rms.save('./state.json', btoa(state), false)
      throw new DOMException(e)
    } finally {
      setTimeout(() => { this.status = 'may' }, 2000)
    }
  }
}
</script>

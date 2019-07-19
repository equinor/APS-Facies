<template>
  <div id="information-bar">
    <v-alert
      :value="shown"
      :type="type"
      dismissible
      transition="slide-y-transition"
      @input="shown = false"
    >{{ message }}</v-alert><!-- eslint-disable-line vue/multiline-html-element-content-newline -->
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'

import { delay } from 'lodash'

import BaseMessage from '@/utils/domain/messages/base'

@Component
export default class InformationBar extends Vue {
  shown: boolean = false

  get _message () {
    return this.$store.state.message.value || {
      value: null,
      kind: 'info',
    }
  }

  get message () {
    let message = this._message.value
    if (message instanceof Error) {
      if (process.env.NODE_ENV === 'develop') {
        throw message
      } else {
        message = message.message
      }
    }
    if (message) message = message.trim()
    return message
  }

  get type () { return this._message.kind }

  @Watch('_message')
  onUpdate (message: BaseMessage) {
    if (message.value) {
      this.shown = true
      const { use, wait } = this.$store.state.message.autoDismiss
      if (use) {
        delay(() => { this.shown = false }, wait)
      }
    }
  }
}
</script>

<style lang="stylus" scoped>
  #information-bar
    .v-alert
      margin: 0px auto
      border-width: 0 0 0
      white-space pre-line
      line-height 1.0
</style>

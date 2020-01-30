<template>
  <v-dialog
    v-model="dialog"
    :max-width="options.width"
    @keydown.esc="ok()"
    @keydown.enter="ok()"
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
      <v-card-text
        v-if="html"
        v-show="!!message"
        v-html="message"
      />
      <v-card-text
        v-else
        v-show="!!message"
      >
        {{ message }}
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="gray"
          text
          @click.native="ok()"
        >
          OK
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { DialogOptions } from '@/utils/domain/bases/interfaces'
import { Color } from '@/utils/domain/facies/helpers/colors'

@Component
export default class WarningDialog extends Vue {
  dialog = false
  message: string | null = null
  title: string | null = null
  options: DialogOptions = {
    color: (this.$vuetify.theme.themes.light.warning as Color),
    width: 290,
  }

  @Prop({ default: false, type: Boolean })
  readonly html!: boolean

  open (title: string, message: string, options: DialogOptions = {}): void {
    this.dialog = true
    this.title = title
    this.message = message
    this.options = Object.assign(this.options, options)
  }

  ok (): void {
    this.dialog = false
  }
}
</script>

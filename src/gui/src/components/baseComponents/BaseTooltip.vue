<template>
  <v-popover
    trigger="hover"
    :disabled="!_message || disabled"
  >
    <slot />
    <span slot="popover">{{ _message }}</span>
  </v-popover>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({
})
export default class BaseTooltip extends Vue {
  @Prop({ default: '' })
  readonly message!: string

  @Prop({ default: false, type: Boolean })
  readonly disabled!: boolean

  get _message (): string | undefined { return this.message || undefined }
}
</script>

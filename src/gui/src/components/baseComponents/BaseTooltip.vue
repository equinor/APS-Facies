<template>
  <v-popover
    :trigger="trigger"
    :disabled="!_message || disabled"
    :open="_open"
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

  @Prop({ default: 'hover' })
  readonly trigger!: 'hover' | 'manual'

  @Prop({ default: false, type: Boolean })
  readonly disabled!: boolean

  @Prop({ default: false, type: Boolean })
  readonly open!: boolean

  get _open (): boolean | undefined { return this.trigger === 'manual' ? this.open : undefined }
  get _message (): string | undefined { return this.message || undefined }
}
</script>

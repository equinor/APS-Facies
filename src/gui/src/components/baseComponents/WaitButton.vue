<template>
  <v-popover
    :disabled="!tooltipText"
    trigger="hover"
  >
    <v-btn
      :disabled="waiting || disabled"
      :dark="dark"
      :flat="flat"
      :color="color"
      :outline="outline"
      @click="e => $emit('click', e)"
    >
      <slot
        v-if="!title && !waiting"
      />
      <span v-if="!waiting">
        {{ title }}
      </span>
      <span v-else>
        <v-progress-circular indeterminate />
      </span>
    </v-btn>
    <span
      slot="popover"
    >
      {{ tooltipText }}
    </span>
  </v-popover>
</template>

<script lang="ts">
import { Color } from '@/utils/domain/facies/helpers/colors'
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class WaitButton extends Vue {
  @Prop({ default: '' })
  readonly title!: string

  @Prop({ default: '' })
  readonly tooltipText: string

  @Prop({ default: false })
  readonly waiting: boolean

  @Prop({ default: false })
  readonly disabled: boolean

  @Prop({ default: false })
  readonly outline: boolean

  @Prop({ default: false })
  readonly flat: boolean

  @Prop({ default: false })
  readonly dark: boolean

  @Prop({ default: '' })
  readonly color: Color
}
</script>

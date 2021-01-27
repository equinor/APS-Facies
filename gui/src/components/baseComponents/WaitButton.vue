<template>
  <v-popover
    :disabled="!tooltipText"
    trigger="hover"
  >
    <v-btn
      :disabled="waiting || disabled"
      :dark="dark"
      :text="text"
      :color="color"
      :outlined="outlined"
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

  @Prop({ default: false, type: Boolean })
  readonly waiting: boolean

  @Prop({ default: false, type: Boolean })
  readonly disabled: boolean

  @Prop({ default: false, type: Boolean })
  readonly outlined: boolean

  @Prop({ default: false, type: Boolean })
  readonly text: boolean

  @Prop({ default: false, type: Boolean })
  readonly dark: boolean

  @Prop({ default: '' })
  readonly color: Color
}
</script>

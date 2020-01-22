<template>
  <v-btn
    :disabled="disabled || waiting"
    :color="color"
    :dark="dark"
    :large="large"
    :left="left"
    :light="light"
    :right="right"
    :small="small"
    icon
    text
    @click.stop="e => $emit('click', e)"
  >
    <v-icon
      :color="color"
      :dark="dark"
      :large="large"
      :left="left"
      :light="light"
      :medium="medium"
      :right="right"
      :size="size"
      :small="small"
      :x-large="xLarge"
      v-text="fullIconName"
    />
  </v-btn>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Color } from '@/utils/domain/facies/helpers/colors'

@Component
export default class IconButton extends Vue {
  @Prop({ required: true })
  readonly icon!: string

  @Prop({ default: false, type: Boolean })
  readonly waiting!: boolean

  @Prop({ default: false, type: Boolean })
  readonly disabled!: boolean

  @Prop({ default: false, type: Boolean })
  readonly loadingSpinner!: boolean

  @Prop({ default: 'black' })
  readonly color!: Color | undefined

  @Prop({ default: false, type: Boolean })
  readonly dark!: boolean

  @Prop({ default: false, type: Boolean })
  readonly large!: boolean

  @Prop({ default: false, type: Boolean })
  readonly left!: boolean

  @Prop({ default: false, type: Boolean })
  readonly light!: boolean

  @Prop({ default: false, type: Boolean })
  readonly medium!: boolean

  @Prop({ default: false, type: Boolean })
  readonly right!: boolean

  @Prop({ default: undefined })
  readonly size!: number | string | undefined

  @Prop({ default: false, type: Boolean })
  readonly small!: boolean

  @Prop({ default: false, type: Boolean })
  readonly xLarge!: boolean

  get fullIconName (): string {
    if (this.loadingSpinner && this.waiting) {
      return '$vuetify.icons.values.refreshSpinner'
    } else {
      return `$vuetify.icons.values.${this.icon}${this.waiting ? 'Spinner' : ''}`
    }
  }
}
</script>

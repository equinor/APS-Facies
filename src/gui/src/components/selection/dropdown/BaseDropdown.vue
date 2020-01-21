<template>
  <v-select
    v-model="selected"
    :items="items"
    :label="label"
    :disabled="disabled"
    :no-data-text="noDataText"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class BaseDropdown<T> extends Vue {
  @Prop({ required: true })
  readonly label!: string

  @Prop({ required: true })
  readonly items!: string[]

  @Prop({ required: true })
  readonly modelGetter!: () => T

  @Prop({ required: true })
  readonly modelSetter!: (value: T) => void

  @Prop({ default: false })
  readonly disabled!: boolean

  @Prop({ default: '$vuetify.noDataText' })
  readonly noDataText!: string

  get selected (): T { return this.modelGetter() }
  set selected (value: T) { this.modelSetter(value) }
}
</script>

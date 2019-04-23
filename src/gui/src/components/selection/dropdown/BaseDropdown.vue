<template>
  <v-select
    v-model="selected"
    :items="items"
    :label="label"
    :disabled="disabled"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class BaseDropdown<T = any> extends Vue {
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

  get selected () { return this.modelGetter() }
  set selected (value) { this.modelSetter(value) }
}
</script>

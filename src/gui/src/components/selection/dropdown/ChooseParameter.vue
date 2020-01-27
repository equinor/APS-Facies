<template>
  <base-dropdown
    v-if="isShown"
    v-model="selected"
    :items="available"
    :label="label"
    :disabled="isDisabled"
    :warn="warn"
    :warn-even-when-empty="warnEvenWhenEmpty"
    :warn-message="warnMessage"
  />
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/ban-ts-ignore */
import { Component, Prop, Vue } from 'vue-property-decorator'

import BaseDropdown from '@/components/selection/dropdown/BaseDropdown.vue'
import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog.vue'

import { Store } from '@/store/typing'

@Component({
  components: {
    BaseDropdown,
    ConfirmationDialog,
  },
})
export default class ChooseParameter<T> extends Vue {
  @Prop({ required: true })
  readonly label!: string

  @Prop({ required: true })
  readonly parameterType!: string

  @Prop({ default: true })
  readonly hideIfDisabled!: boolean

  @Prop({ default: false })
  readonly disabled!: boolean

  @Prop({ default: false, type: Boolean })
  readonly regular!: boolean

  @Prop({ default: false, type: Boolean })
  readonly warn!: boolean

  @Prop({ default: '' })
  readonly warnMessage!: string

  @Prop({ default: false, type: Boolean })
  readonly warnEvenWhenEmpty: boolean

  get available (): T[] { return (this.$store as Store).state.parameters[this.parameterType].available }
  get isDisabled (): boolean { return (!this.regular && this.available ? this.available.length <= 1 : false) || this.disabled }
  get isShown (): boolean { return !(this.hideIfDisabled && this.isDisabled) }

  get selected (): T { return (this.$store as Store).state.parameters[this.parameterType].selected }
  set selected (value: T) { this.$store.dispatch(`parameters/${this.parameterType}/select`, value) }
}
</script>

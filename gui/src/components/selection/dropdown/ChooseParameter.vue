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
import { Component, Prop, Vue } from 'vue-property-decorator'

import BaseDropdown from '@/components/selection/dropdown/BaseDropdown.vue'
import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog.vue'

import { Store } from '@/store/typing'
import { ListItem } from '@/utils/typing'

@Component({
  components: {
    BaseDropdown,
    ConfirmationDialog,
  },
})
export default class ChooseParameter extends Vue {
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

  get available (): ListItem<string>[] {
    return this.$store.state.parameters[this.parameterType].available
      .map((item: string): ListItem<string> => ({
        text: item,
        value: item,
      }))
  }

  get isDisabled (): boolean { return (!this.regular && this.available ? this.available.length <= 1 : false) || this.disabled }
  get isShown (): boolean { return !(this.hideIfDisabled && this.isDisabled) }

  get selected (): string { return (this.$store as Store).state.parameters[this.parameterType].selected }
  set selected (value: string) { this.$store.dispatch(`parameters/${this.parameterType}/select`, value) }
}
</script>

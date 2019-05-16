<template>
  <base-dropdown
    v-if="isShown"
    :items="available"
    :model-getter="getter"
    :model-setter="setter"
    :disabled="isDisabled"
    :label="label"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import BaseDropdown from '@/components/selection/dropdown/BaseDropdown.vue'

import { Store } from '@/store/typing'

@Component({
  components: {
    BaseDropdown
  },
})
export default class ChooseParameter<T = any> extends Vue {
  @Prop({ required: true })
  readonly label!: string

  @Prop({ required: true })
  readonly parameterType!: string

  @Prop({ default: true })
  readonly hideIfDisabled!: boolean

  @Prop({ default: false })
  readonly disabled!: boolean

  get available (): T[] { return (this.$store as Store).state.parameters[this.parameterType].available }
  get selected (): T { return (this.$store as Store).state.parameters[this.parameterType].selected }
  get isDisabled (): boolean { return (this.available ? this.available.length <= 1 : false) || this.disabled }
  get isShown (): boolean { return !(this.hideIfDisabled && this.isDisabled) }

  getter () { return this.selected }
  setter (value: T) { this.$store.dispatch(`parameters/${this.parameterType}/select`, value) }
}
</script>

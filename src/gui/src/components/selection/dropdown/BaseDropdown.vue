<template>
  <div>
    <confirmation-dialog
      v-if="warn"
      ref="confirm"
    />
    <v-select
      ref="selection"
      v-model.lazy="selected"
      :items="items"
      :disabled="disabled"
      :label="label"
    />
  </div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/ban-ts-ignore */
import { Component, Prop, Vue } from 'vue-property-decorator'

import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog.vue'

import { ListItem } from '@/utils/typing'

@Component({
  components: {
    ConfirmationDialog,
  },
})
export default class BaseDropdown<T> extends Vue {
  @Prop({ required: true })
  readonly value!: T

  @Prop({ required: true })
  readonly label!: string

  @Prop({ required: true })
  readonly items!: ListItem<T>[] | T[]

  @Prop({ default: false })
  readonly disabled!: boolean

  @Prop({ default: false, type: Boolean })
  readonly warn!: boolean

  @Prop({ default: '' })
  readonly warnMessage!: string

  @Prop({ default: false, type: Boolean })
  readonly warnEvenWhenEmpty: boolean

  get selected (): T { return this.value }
  set selected (value: T) {
    const changeValue = (): void => { this.$emit('input', value) }

    if (this.warn && (!!this.selected || this.warnEvenWhenEmpty)) {
      // @ts-ignore
      (this.$refs.confirm as ConfirmationDialog).open('Are you sure?', this.warnMessage)
        .then((confirmed: boolean) => {
          if (confirmed) changeValue()
          else {
            // The component must be made aware that its value was not updated
            // @ts-ignore
            this.$refs.selection.lazyValue = this.selected
          }
        })
    } else {
      changeValue()
    }
  }
}
</script>

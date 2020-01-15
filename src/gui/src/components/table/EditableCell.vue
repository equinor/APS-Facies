<template>
  <v-edit-dialog
    lazy
    @open="reset"
  >
    <highlight-current-item
      :value="value"
      :current="current"
      :field="field"
    />
    <v-text-field
      slot="input"
      v-model="$data._fieldValue"
      :label="label"
      single-line
      @keydown.enter="submit"
    />
  </v-edit-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import HighlightCurrentItem from '@/components/baseComponents/HighlightCurrentItem.vue'

import { ID } from '@/utils/domain/types'

@Component({
  components: {
    HighlightCurrentItem,
  }
})
export default class EditableCell<T> extends Vue {
  _fieldValue: string = this.fieldValue

  @Prop({ required: true })
  readonly value: T

  @Prop({ required: true })
  readonly field: string

  @Prop({ required: false, default: 'Edit' })
  readonly label: string

  @Prop({ required: true })
  readonly current: ID

  get fieldValue (): string { return this.value[this.field] }

  submit () {
    this.$emit('submit', {
      ...this.value,
      [this.field]: this.$data._fieldValue
    })
  }

  reset () {
    this.$data._fieldValue = this.fieldValue
  }
}
</script>

<template>
  <v-edit-dialog
    lazy
    @open="reset"
  >
    {{ value[field] }}
    <v-text-field
      slot="input"
      v-model="$data._fieldValue"
      :label="label"
      :type="numeric ? 'number' : 'text'"
      single-line
      @keydown.enter="submit"
    />
  </v-edit-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({
})
export default class EditableCell<T> extends Vue {
  _fieldValue: string = this.fieldValue

  @Prop({ required: true })
  readonly value: T

  @Prop({ required: true })
  readonly field: string

  @Prop({ required: false, default: 'Edit' })
  readonly label: string

  @Prop({ default: false, type: Boolean })
  readonly numeric: boolean

  get fieldValue (): string { return this.value[this.field] }

  submit (): void {
    const value = this.$data._fieldValue
    this.$emit('submit', {
      ...this.value,
      [this.field]: this.numeric ? Number(value) : value,
    })
  }

  reset (): void {
    this.$data._fieldValue = this.fieldValue
  }
}
</script>

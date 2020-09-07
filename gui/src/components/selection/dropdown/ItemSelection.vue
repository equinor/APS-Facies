<template>
  <v-select
    :value="value"
    :items="items"
    :label="label"
    :error-messages="errors"
    @blur="$v.value.$touch()"
    @input.capture="e => $emit('input', e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { required } from 'vuelidate/lib/validators'

/* TODO: Remove // @ts-ignore when vuelidate OFFICIALLY  supports TypeScript */

@Component({
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  validations<T> () {
    return {
      value: {
        required: (this as ItemSelection<T>).constraints.required ? required : true,
        legalChoice: (this as ItemSelection<T>).items.includes((this as ItemSelection<T>).value)
      },
    }
  },
})
export default class ItemSelection<T> extends Vue {
  @Prop({ required: true })
  value: T

  @Prop({ required: true })
  items: T[]

  @Prop({ default: '' })
  label: string

  @Prop()
  constraints: {
    required: boolean
    legalChoice: boolean
    [_: string]: any
  }

  get errors (): string[] {
    if (!this.$v.value) return []

    const errors: string[] = []
    if (!this.$v.value.$dirty) return errors
    !this.$v.value.required && errors.push('Is required')
    !this.$v.value.legalChoice && errors.push('Illegal choice')
    return errors
  }

  @Watch('$v.$invalid')
  onInvalidChanged (value: boolean): void {
    this.$emit('update:error', value)
  }
}
</script>

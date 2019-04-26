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
import { Component, Prop, Vue } from 'vue-property-decorator'
import { required } from 'vuelidate/lib/validators'

/* TODO: Remove // @ts-ignore when vuelidate OFFICIALLY  supports TypeScript */

@Component({
// @ts-ignore
  validations () {
    return {
      value: {
        // @ts-ignore
        required: this.constraints.required ? required : true,
      },
    }
  },
})
export default class ItemSelection<T = any> extends Vue {
  @Prop({ required: true })
  value: T

  @Prop({ required: true })
  items: T[]

  @Prop({ default: '' })
  label: string

  @Prop()
  constraints: {
    required: boolean
    [_: string]: any
  }

  get errors (): string[] {
    const errors: string[] = []
    // @ts-ignore
    if (!this.$v.value.$dirty) return errors
    // @ts-ignore
    !this.$v.value.required && errors.push('Is required')
    return errors
  }
}
</script>

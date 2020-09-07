<template>
  <v-text-field
    v-model="fieldName"
    :error-messages="errors"
    @click.stop
    @input="$v.fieldName.$touch()"
    @blur="$v.fieldName.$touch()"
  />
</template>
<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { required } from 'vuelidate/lib/validators'
import { GaussianRandomField } from '@/utils/domain'
import { Optional } from '@/utils/typing'

@Component({
  validations () {
    return {
      fieldName: {
        required,
        isUnique (value): boolean {
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          const current = this.value.id
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          return !this.fields.some(({ name, id }: GaussianRandomField) => name === value && id !== current)
        },
      },
    }
  },
})
export default class GaussianFieldName extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  fieldName: Optional<string> = null

  get fields (): GaussianRandomField[] { return this.$store.getters.fields }

  get name (): string { return this.value.name }

  get errors (): string[] {
    if (!this.$v.fieldName) return []

    const errors: string[] = []
    if (!this.$v.fieldName.$dirty) return errors
    !this.$v.fieldName.required && errors.push('Is required')
    !this.$v.fieldName.isUnique && errors.push('Must be unique')
    return errors
  }

  @Watch('fieldName')
  onNameChange (value: string): void {
    if (this.$v.fieldName && !this.$v.fieldName.$invalid) {
      this.$store.dispatch('gaussianRandomFields/changeName', { field: this.value, name: value })
    }
  }

  mounted (): void {
    this.fieldName = this.name
  }
}
</script>

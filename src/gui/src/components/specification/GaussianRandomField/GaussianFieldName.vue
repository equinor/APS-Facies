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
        isUnique (value) {
          // @ts-ignore
          const current = this.value.id
          // @ts-ignore
          return !this.fields.some(({ name, id }) => name === value && id !== current)
        },
      },
    }
  },
})
export default class GaussianFieldName extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  fieldName: Optional<string> = null

  get fields () { return Object.values(this.$store.state.gaussianRandomFields.available) }

  get name () { return this.value.name }

  get errors () {
    const errors: string[] = []
    // @ts-ignore
    if (!this.$v.fieldName.$dirty) return errors
    // @ts-ignore
    !this.$v.fieldName.required && errors.push('Is required')
    // @ts-ignore
    !this.$v.fieldName.isUnique && errors.push('Must be unique')
    return errors
  }

  @Watch('fieldName')
  onNameChange (value: string) {
    // @ts-ignore
    if (!this.$v.fieldName.$invalid) {
      this.$store.dispatch('gaussianRandomFields/changeName', { field: this.value, name: value })
    }
  }

  mounted () {
    this.fieldName = this.name
  }
}
</script>

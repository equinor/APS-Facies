<template>
  <v-text-field
    v-model="fieldName"
    :error-messages="errors"
    @click.stop
    @input="$v.fieldName.$touch()"
    @blur="$v.fieldName.$touch()"
  />
</template>
<script>
import { required } from 'vuelidate/lib/validators'
import { AppTypes } from '@/utils/typing'

export default {
  props: {
    value: AppTypes.gaussianRandomField.isRequired,
  },

  data () {
    return {
      fieldName: null,
    }
  },

  validations: {
    fieldName: {
      required,
      isUnique (value) {
        const current = this.value.id
        return !Object.values(this.fields).some(({ name, id }) => name === value && id !== current)
      },
    },
  },

  computed: {
    fields () { return this.$store.state.gaussianRandomFields.available },
    name () { return this.value.name },
    errors () {
      const errors = []
      if (!this.$v.fieldName.$dirty) return errors
      !this.$v.fieldName.required && errors.push('Is required')
      !this.$v.fieldName.isUnique && errors.push('Must be unique')
      return errors
    },
  },

  watch: {
    fieldName (value) {
      if (!this.$v.fieldName.$invalid) {
        this.$store.dispatch('gaussianRandomFields/changeName', { grfId: this.value.id, name: value })
      }
    }
  },

  mounted () {
    this.fieldName = this.name
  },
}
</script>

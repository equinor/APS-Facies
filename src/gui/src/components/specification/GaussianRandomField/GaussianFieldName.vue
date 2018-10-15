<template>
  <v-text-field
    v-model="fieldName"
    :error-messages="errors"
    @click.stop
    @keydown.esc="restoreName"
    @keydown.enter="changeName"
    @input="$v.fieldName.$touch()"
    @blur="$v.fieldName.$touch()"
  />
</template>
<script>
import VueTypes from 'vue-types'
import { required } from 'vuelidate/lib/validators'

// TODO: Add description of behavior
// Alt; make behavior consistent with remaining application
export default {
  props: {
    grfId: VueTypes.string.isRequired,
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
        for (const grfId in this.fields) {
          if (this.fields[`${grfId}`].name === value && this.grfId !== grfId) {
            return false
          }
        }
        return true
      },
    }
  },

  computed: {
    fields () { return this.$store.state.gaussianRandomFields.fields },
    name () { return this.fields[this.grfId].name },
    errors () {
      const errors = []
      if (!this.$v.fieldName.$dirty) return errors
      !this.$v.fieldName.required && errors.push('Is required')
      !this.$v.fieldName.isUnique && errors.push('Must be unique')
      return errors
    },
  },

  mounted () {
    this.fieldName = this.name
  },

  methods: {
    changeName () {
      this.$store.dispatch('gaussianRandomFields/changeName', { grfId: this.grfId, name: this.fieldName })
    },
    restoreName () {
      this.fieldName = this.name
    },
  },
}
</script>

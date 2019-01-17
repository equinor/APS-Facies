<template>
  <v-text-field
    v-model="fieldName"
    :error-messages="errors"
    :hint="showTip"
    @click.stop
    @keydown.esc="restoreName"
    @keydown.enter="changeName"
    @input="$v.fieldName.$touch()"
    @blur="$v.fieldName.$touch()"
  />
</template>
<script>
import { required } from 'vuelidate/lib/validators'
import { AppTypes } from '@/utils/typing'

// TODO: Add description of behavior
//       Alt; make behavior consistent with remaining application
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
        const current = { name: this.name, id: this.value.id }
        return !Object.values(this.fields).some(({ name, id }) => name === value && id !== current.id)
      },
    },
  },

  computed: {
    fields () { return this.$store.state.gaussianRandomFields.fields },
    name () { return this.value.name },
    errors () {
      const errors = []
      if (!this.$v.fieldName.$dirty) return errors
      !this.$v.fieldName.required && errors.push('Is required')
      !this.$v.fieldName.isUnique && errors.push('Must be unique')
      return errors
    },
    showTip () {
      if (this.name !== this.fieldName) {
        return 'Press enter to save'
      } else {
        return ''
      }
    },
  },

  mounted () {
    this.fieldName = this.name
  },

  methods: {
    changeName () {
      this.$store.dispatch('gaussianRandomFields/changeName', { grfId: this.value.id, name: this.fieldName })
    },
    restoreName () {
      this.fieldName = this.name
    },
  },
}
</script>

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

<script>
import Vue from 'vue'
import VueTypes from 'vue-types'
import { required } from 'vuelidate/lib/validators'

export default Vue.extend({
  name: 'ItemSelection',

  props: {
    value: VueTypes.any.isRequired,
    items: VueTypes.arrayOf(VueTypes.any).isRequired,
    label: VueTypes.string,
    constraints: VueTypes.shape({
      required: VueTypes.bool,
    }).loose
  },

  validations () {
    return {
      value: {
        required: this.constraints.required ? required : true,
      },
    }
  },

  computed: {
    errors () {
      const errors = []
      if (!this.$v.value.$dirty) return errors
      !this.$v.value.required && errors.push('Is required')
      return errors
    },
  },
})
</script>

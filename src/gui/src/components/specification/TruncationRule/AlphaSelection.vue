<template>
  <v-select
    v-model="selected"
    :items="fieldNames"
  >
    <template
      slot="label"
    >
      <span>α<sub>{{ channel }}</sub></span>
    </template>
  </v-select>
</template>

<script>
import { mapGetters } from 'vuex'

import VueTypes from 'vue-types'

// TODO: Implement check that gives a warning/error when the same GRF is used more than once
export default {
  props: {
    value: VueTypes.oneOfType([VueTypes.string, null]).isRequired,
    channel: VueTypes.integer.isRequired,
  },

  computed: {
    ...mapGetters({
      fields: 'fields'
    }),
    selected: {
      get: function () {
        return this.fieldNames.find(item => item.value === this.value)
          ? this.value
          : null
      },
      set: function (value) { this.$emit('input', value) },
    },
    fieldNames () {
      return Object.values(this.fields)
        .map(field => {
          return {
            text: field.name,
            value: field.id,
          }
        })
    }
  }
}
</script>

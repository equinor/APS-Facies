<template>
  <v-select
    v-model="selected"
    :items="fieldNames"
    clearable
  >
    <template
      v-if="!hideLabel"
      slot="label"
    >
      <span>α<sub>{{ channel }}</sub></span>
    </template>
  </v-select>
</template>

<script>
import { mapGetters } from 'vuex'

import VueTypes from 'vue-types'
import { AppTypes } from '@/utils/typing'

export default {
  props: {
    value: VueTypes.oneOfType([AppTypes.id, null]).isRequired,
    channel: VueTypes.integer.isRequired,
    hideLabel: VueTypes.bool.def(false),
  },

  computed: {
    ...mapGetters({
      rule: 'truncationRule',
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
          const disabled = this.rule
            ? this.rule.fields
              .findIndex(inRule => (
                inRule.field === field.id &&
                inRule.channel !== this.channel
              )) >= 0
            : false
          return {
            text: field.name,
            value: field.id,
            disabled,
          }
        })
    }
  }
}
</script>

<template>
  <v-select
    v-model="selected"
    :items="fields"
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
    rule: AppTypes.truncationRule.isRequired,
    channel: VueTypes.integer.isRequired,
    group: AppTypes.id.def(''),
    hideLabel: VueTypes.bool.def(false),
  },

  computed: {
    ...mapGetters({
      _fields: 'fields'
    }),
    selected: {
      get: function () {
        return this.fields.find(item => item.value === this.value)
          ? this.value
          : null
      },
      set: function (value) { this.$emit('input', value) },
    },
    fields () {
      return Object.values(this._fields)
        .map(field => {
          const disabled = this.rule
            ? this.rule.fields
              .findIndex(inRule => (
                inRule.field === field.id &&
                inRule.channel !== this.channel
              )) >= 0 && (
              this.group && !this.rule.backgroundFields.some(background => background.field === field.id)
                ? this.rule.overlayPolygons
                  .filter(({ group }) => group === this.group)
                  .some(polygon => polygon.field === field.id)
                : true
            )
            : false
          return {
            text: field.name,
            value: field.id,
            disabled: disabled && this.value !== field.id,
          }
        })
    }
  }
}
</script>

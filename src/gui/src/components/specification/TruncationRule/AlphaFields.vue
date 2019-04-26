<template>
  <v-layout>
    <v-flex
      v-for="item in alphas"
      :key="item.channel"
      pa-1
    >
      <alpha-selection
        :channel="item.channel"
        :value="item.selected"
        :rule="value"
        group=""
        @input="val => update(item, val)"
      />
    </v-flex>
  </v-layout>
</template>

<script>
import VueTypes from 'vue-types'

import { AppTypes } from '@/utils/typing'

import AlphaSelection from './AlphaSelection'

const defaultChannels = (num) => {
  const items = []
  for (let i = 1; i <= num; i++) {
    // NOTE: The alpha channels are (supposed to be) 1-indexed
    items.push({ channel: i, selected: '' })
  }
  return items
}

export default {
  components: {
    AlphaSelection,
  },

  props: {
    value: AppTypes.truncationRule,
    minFields: VueTypes.integer.def(2),
  },

  computed: {
    alphas () {
      return this.value
        ? this.value.backgroundFields
          .map((field, index) => {
            return {
              channel: index + 1,
              selected: field
            }
          })
        : defaultChannels(this.minFields)
    },
  },

  methods: {
    update ({ channel }, fieldId) {
      const field = this.$store.state.gaussianRandomFields.fields[`${fieldId}`]
      return this.$store.dispatch('truncationRules/updateBackgroundField', {
        index: channel - 1,
        rule: this.value,
        field: field || null
      })
    }
  },
}
</script>

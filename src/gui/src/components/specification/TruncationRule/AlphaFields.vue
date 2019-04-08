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
import { sortByProperty } from '@/utils'

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
    minChannels: VueTypes.integer.def(2),
  },

  computed: {
    alphas () {
      return this.value
        ? sortByProperty('channel')(this.value.backgroundFields)
          .map(item => {
            return {
              channel: item.channel,
              selected: item.field || '' }
          })
        : defaultChannels(this.minChannels)
    },
  },

  methods: {
    update (item, value) {
      return this.$store.dispatch('truncationRules/updateFields', { channel: item.channel, selected: value })
    }
  },
}
</script>

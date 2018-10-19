<template>
  <div>
    <alpha-selection
      v-for="item in alphas"
      :key="item.channel"
      :channel="item.channel"
      :value="item.selected"
      @input="value => update(item, value)"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import VueTypes from 'vue-types'

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
    minChannels: VueTypes.integer.def(2)
  },

  computed: {
    ...mapGetters({
      rule: 'truncationRule',
    }),
    alphas () {
      return this.rule
        ? this.rule.fields
          .map(item => { return { channel: item.channel, selected: item.field || '' } })
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

<style scoped>

</style>

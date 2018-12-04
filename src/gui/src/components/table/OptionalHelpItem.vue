<template>
  <div>
    <v-tooltip
      v-if="hasHelp"
      bottom
    >
      <span slot="activator">
        {{ text }}
      </span>
      <span>
        {{ help }}
      </span>
    </v-tooltip>
    <span v-else>{{ text }}</span>
  </div>
</template>

<script>
import VueTypes from 'vue-types'
import { notEmpty } from '@/utils'

export default {
  props: {
    value: VueTypes.oneOfType([
      VueTypes.shape({
        text: VueTypes.string.isRequired,
        help: VueTypes.string,
      }).loose,
      VueTypes.shape({
        name: VueTypes.string.isRequired,
        help: VueTypes.string,
      }).loose,
      VueTypes.string,
      VueTypes.number,
    ]).isRequired
  },

  computed: {
    text () { return this.value.text || this.value.name || this.value },
    help () { return this.value.help },
    hasHelp () {
      return notEmpty(this.value.help)
    }
  }
}
</script>

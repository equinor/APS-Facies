<template>
  <v-btn
    :disabled="disabled || waiting"
    icon
    @click.stop="e => $emit('click', e)"
  >
    <v-icon v-text="fullIconName"/>
  </v-btn>
</template>

<script>
import VueTypes from 'vue-types'

export default {
  props: {
    icon: VueTypes.string.isRequired,
    waiting: VueTypes.bool.def(false),
    disabled: VueTypes.bool.def(false),
  },

  computed: {
    fullIconName () {
      return `$vuetify.icons.${this.icon}${this.waiting ? 'Spinner' : ''}`
    }
  },
}
</script>

<style scoped>

</style>

<template>
  <v-btn
    :disabled="disabled"
    :dark="dark"
    :color="color"
    @click="e => $emit('click', e)"
  >
    <span v-if="!waiting">{{ title }}</span>
    <span v-else><v-progress-circular indeterminate/></span>
  </v-btn>
</template>

<script>
import VueTypes from 'vue-types'

export default {
  name: 'WaitBtn',

  props: {
    title: VueTypes.string.isRequired,
    waiting: VueTypes.bool.def(false),
    disabled: VueTypes.bool.def(false),
    dark: VueTypes.bool.def(false),
    color: VueTypes.string,
  },
}
</script>

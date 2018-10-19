<template>
  <v-btn
    :disabled="disabled"
    icon
    @click.stop="e => $emit('click', e)"
  >
    <v-icon v-text="icon"/>
  </v-btn>
</template>

<script>
import VueTypes from 'vue-types'

export default {
  props: {
    icon: VueTypes.string.isRequired,
    disabled: VueTypes.bool.def(false),
  },
}
</script>

<style scoped>

</style>

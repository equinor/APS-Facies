<template>
  <v-btn
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
  },
}
</script>

<style scoped>

</style>

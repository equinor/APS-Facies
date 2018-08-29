<template>
  <v-btn
    color="primary"
    dark
    @click="e => $emit('click', e)">{{ title }}</v-btn>
</template>

<script>

import VueTypes from 'vue-types'

export default {
  props: {
    title: VueTypes.string.required
  },
}

</script>

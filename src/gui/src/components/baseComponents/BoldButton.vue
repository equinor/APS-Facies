<template>
  <wait-btn
    :title="title"
    color="primary"
    dark
    @click="e => $emit('click', e)"
  />
</template>

<script>

import VueTypes from 'vue-types'
import WaitBtn from '@/components/baseComponents/WaitButton'

export default {
  components: {
    WaitBtn
  },

  props: {
    title: VueTypes.string.required
  },
}

</script>

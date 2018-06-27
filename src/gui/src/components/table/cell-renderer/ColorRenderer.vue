<template>
  <span/>
</template>

<script>
import Vue from 'vue'

export default Vue.extend({
  data () {
    return {
      color: null
    }
  },
  created () {
    this.setColor(this.params)
  },

  methods: {
    refresh (params) {
      this.params = params
      return true
    },
    setColor (params) {
      this.color = params.value
    }
  }
})
</script>

<style scoped>

</style>

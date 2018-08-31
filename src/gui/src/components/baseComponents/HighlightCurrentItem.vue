<template>
  <span :class="item.current ? 'font-weight-bold' : ''">
    {{ item[field] }}
  </span>
</template>

<script>
import VueTypes from 'vue-types'

export default {
  props: {
    item: VueTypes.shape({
      current: VueTypes.bool.isRequired,
    }).loose.isRequired,
    field: VueTypes.string.isRequired,
  }
}
</script>

<style scoped>

</style>

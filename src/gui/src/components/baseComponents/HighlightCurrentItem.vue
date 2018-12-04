<template>
  <span :class="item.current ? 'font-weight-bold' : ''">
    {{ item[field] }}
  </span>
</template>

<script>
import VueTypes from 'vue-types'
import { AppTypes } from '@/utils/typing'

export default {
  props: {
    item: VueTypes.shape({
      current: VueTypes.bool.isRequired,
    }).loose.isRequired,
    field: AppTypes.name.isRequired,
  }
}
</script>

<style scoped>

</style>

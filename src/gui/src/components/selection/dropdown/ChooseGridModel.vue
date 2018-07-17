<template>
  <base-dropdown
    :items="available"
    :model-getter="getter"
    :model-setter="setter"
    label="Grid model"
  />
</template>

<script>
import BaseDropdown from '@/components/selection/dropdown/BaseDropdown'

export default {
  components: {
    BaseDropdown: BaseDropdown
  },

  computed: {
    available () {
      return this.$store.state.gridModels.available
    },
  },

  beforeMount () {
    this.$store.dispatch('gridModels/fetch')
  },

  methods: {
    getter () {
      return this.$store.state.gridModels.current
    },
    setter (value) {
      this.$store.dispatch('gridModels/select', value)
    }
  },
}
</script>

<style scoped>

</style>

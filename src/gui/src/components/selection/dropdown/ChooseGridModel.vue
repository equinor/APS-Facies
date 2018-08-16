<template>
  <base-dropdown
    :items="available"
    :model-getter="getter"
    :model-setter="setter"
    label="Grid model"
  />
</template>

<script>
import BaseDropdown from 'Components/selection/dropdown/BaseDropdown'

export default {
  components: {
    BaseDropdown: BaseDropdown
  },

  computed: {
    available () {
      return this.$store.state.gridModels.available
    },
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

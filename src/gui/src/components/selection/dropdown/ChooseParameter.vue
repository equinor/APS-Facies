<template>
  <base-dropdown
    :items="available"
    :model-getter="getter"
    :model-setter="setter"
    :disabled="isDisabled"
    :label="label"
  />
</template>

<script>
import VueTypes from 'vue-types'
import BaseDropdown from '@/components/selection/dropdown/BaseDropdown'

export default {
  components: {
    BaseDropdown
  },

  props: {
    label: VueTypes.string.isRequired,
    parameterType: VueTypes.string.isRequired,
    disabled: VueTypes.bool.def(false)
  },

  computed: {
    available () { return this.$store.state.parameters[this.parameterType].available },
    selected () { return this.$store.state.parameters[this.parameterType].selected },
    isDisabled () { return (this.available ? this.available.length <= 1 : false) || this.disabled },
  },

  methods: {
    getter () {
      return this.selected
    },
    setter (value) {
      this.$store.dispatch(`parameters/${this.parameterType}/select`, value)
    }
  },
}
</script>

<style scoped>

</style>

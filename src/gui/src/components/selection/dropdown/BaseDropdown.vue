<template>
  <v-select
    v-model="selected"
    :items="items"
    :label="label"
    :disabled="disabled"
  />
</template>

<script>
import VueTypes from 'vue-types'

export default {
  props: {
    label: VueTypes.string.isRequired,
    items: VueTypes.arrayOf(VueTypes.string).isRequired,
    modelGetter: VueTypes.func.isRequired,
    modelSetter: VueTypes.func.isRequired,
    disabled: VueTypes.bool.def(false),
  },

  computed: {
    selected: {
      get () {
        return this.modelGetter()
      },
      set (value) {
        this.modelSetter(value)
      }
    }
  }
}
</script>

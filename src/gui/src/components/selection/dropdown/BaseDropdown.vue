<template>
  <v-container>
    <v-flex
      xs12
      sm6
      d-flex
    >
      <v-select
        :items="items"
        v-model="selected"
        :label="label"
        :disabled="disabled"
      />
    </v-flex>
  </v-container>
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

<style scoped>

</style>

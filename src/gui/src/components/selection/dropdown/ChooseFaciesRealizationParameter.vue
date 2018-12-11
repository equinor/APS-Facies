<template>
  <v-combobox
    v-model="faciesRealizationParameter"
    :items="available"
    :append-icon="''"
    :append-outer-icon="'$vuetify.icons.search'"
    label="Facies Realisation parameter"
  />
</template>

<script>
export default {
  name: 'ChooseFaciesRealizationParameter',

  computed: {
    faciesRealizationParameter: {
      get: function () { return this.$store.state.parameters.realization.selected },
      set: async function (value) { await this.$store.dispatch('parameters/realization/select', value) },
    },
    available () {
      return this.$store.state.parameters.realization.available
    },
  },
}
</script>

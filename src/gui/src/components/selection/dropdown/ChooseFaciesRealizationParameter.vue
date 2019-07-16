<template>
  <v-combobox
    v-model="faciesRealizationParameter"
    :items="available"
    :append-icon="''"
    :append-outer-icon="'$vuetify.icons.search'"
    label="Facies Realization parameter"
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class ChooseFaciesRealizationParameter extends Vue {
  get faciesRealizationParameter () { return this.$store.state.parameters.realization.selected }
  set faciesRealizationParameter (value) { this.$store.dispatch('parameters/realization/select', value) }

  get available () { return this.$store.state.parameters.realization.available }
}
</script>

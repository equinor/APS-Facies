<template>
  <v-container fluid>
    <v-layout row>
      <v-flex
        xs3
        center
      >
        <v-card-text>Grid</v-card-text>
      </v-flex>
      <v-flex xs9>
        <v-select
          :items="availableGridModels"
          v-model="selectedGridModel"
          item-text="name"
          single-line
        />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  computed: {
    availableGridModels () {
      return this.$store.getters.availableGridModelNames
    },

    selectedGridModel: {
      get () {
        return this.$store.state.selectedGridModel
      },
      set (value) {
        this.$store.dispatch('selectGridModel', {selectedGridModel: value})
      }
    }
  },
}
</script>

<style scoped>

</style>

<template>
  <v-container fluid>
    <v-layout wrap>
      <v-flex xs4><Selection/></v-flex>
      <v-flex xs4><Preview/></v-flex>
      <v-flex xs4><Settings/></v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import Selection from 'Components/ElementSelection'
import Settings from 'Components/ElementSettings'
import Preview from 'Components/ElementPreview'
import GaussianRandomFields from 'Components/specification/GaussianRandomField/multiple'

export default {
  components: {
    GaussianRandomFields,
    Selection,
    Settings,
    Preview
  }
}
</script>

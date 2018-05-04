<template>
  <v-container fluid>
    <v-layout wrap>
      <v-flex><Selection/></v-flex>
      <v-flex><Preview/></v-flex>
      <v-flex><Settings/></v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import Selection from '@/components/ElementSelection'
import Settings from '@/components/ElementSettings'
import Preview from '@/components/ElementPreview'

export default {
  components: {
    Selection,
    Settings,
    Preview
  }
}
</script>

<style scoped>

</style>

<template>
  <v-container fluid>
    <v-layout wrap>
      <v-flex xs4><Selection/></v-flex>
      <v-flex xs4><Preview/></v-flex>
      <v-flex xs4>
        <Settings
          v-if="zoneSelected"
        />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import Selection from '@/components/ElementSelection'
import Settings from '@/components/ElementSettings'
import Preview from '@/components/ElementPreview'
import GaussianRandomFields from '@/components/specification/GaussianRandomField/multiple'

export default {
  components: {
    GaussianRandomFields,
    Selection,
    Settings,
    Preview
  },

  computed: {
    zoneSelected () {
      return !!this.$store.getters.zone
    }
  }
}
</script>

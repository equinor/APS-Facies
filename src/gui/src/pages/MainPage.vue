<template>
  <v-container fluid>
    <v-layout wrap>
      <v-flex xs4><Selection/></v-flex>
      <v-flex xs4><Preview v-if="hasSimulations"/></v-flex>
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

export default {
  components: {
    Selection,
    Settings,
    Preview
  },

  computed: {
    fields () {
      return Object.values(this.$store.getters.fields)
    },
    zoneSelected () {
      return !!this.$store.getters.zone
    },
    hasSimulations () {
      return this.fields.length > 0 && this.fields.every(field => field._data.length > 0 && field._data[0].length > 0)
    },
  }
}
</script>

<template>
  <v-layout
    column
  >
    <v-layout
      align-center
      justify-space-between
      row
      fill-height
    >
      <h3>Overlay Facies</h3>
    </v-layout>
    <overlay-facies-table
      :value="value"
    />
  </v-layout>
</template>

<script>
import OverlayFaciesTable from './table'
import { AppTypes } from '@/utils/typing'

export default {
  components: {
    OverlayFaciesTable,
  },

  props: {
    value: AppTypes.truncationRule.isRequired,
  },
}
</script>

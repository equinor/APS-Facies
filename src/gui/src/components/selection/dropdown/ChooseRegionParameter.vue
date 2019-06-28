<template>
  <v-layout
    row
  >
    <v-checkbox
      v-model="useRegions"
      label="Use regions?"
    />
    <choose-parameter
      :disabled="!useRegions"
      regular
      parameter-type="region"
      label="Region parameter"
    />
  </v-layout>
</template>

<script>
import ChooseParameter from '@/components/selection/dropdown/ChooseParameter'

export default {
  components: {
    ChooseParameter
  },

  computed: {
    useRegions: {
      cache: false,
      get: function () {
        return this.$store.state.regions.use
      },
      set: function (value) {
        this.$store.dispatch('regions/use', { use: value })
      }
    },
  }
}
</script>

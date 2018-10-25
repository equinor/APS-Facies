<template>
  <v-select
    :items="faciesOptions"
    :value="value"
    :multiple="multiple"
    @input.capture="facies => $emit('input', facies)"
  />

</template>

<script>
import { mapGetters } from 'vuex'

import VueTypes from 'vue-types'
import { AppTypes } from '@/utils/typing'

export default {
  name: 'FaciesSpecificationBase',

  props: {
    value: VueTypes.oneOfType([AppTypes.id, AppTypes.ids]).isRequired,
    multiple: VueTypes.bool.def(false),
    rule: AppTypes.truncationRule,
  },

  computed: {
    ...mapGetters({
      selectedFacies: 'facies/selected',
    }),
    faciesOptions () {
      return this.selectedFacies
        .map(facies => {
          return {
            text: facies.name,
            value: facies.id,
            disabled: this.multiple
              ? this.rule.overlayPolygons.map(polygon => polygon.facies).indexOf(facies.id) >= 0
              : false,
          }
        })
    },
  },
}
</script>

<template>
  <realization-map
    :data="data"
    :color-scale="faciesColors"
    :expand="expand"
  />
</template>

<script>
import { mapGetters } from 'vuex'
import VueTypes from 'vue-types'

import RealizationMap from '@/components/plot/GaussianPlot'
import IconButton from '@/components/selection/IconButton'

export default {
  name: 'FaciesRealization',
  components: {
    IconButton,
    RealizationMap,
  },

  props: {
    expand: VueTypes.bool.def(false),
  },

  computed: {
    ...mapGetters({
      rule: 'truncationRule',
      fields: 'fields',
    }),
    data () {
      return this.rule && this.rule._realization
        ? this.rule._realization
        : []
    },
    fields () {
      const fields = this.$store.getters.fields
      return this.rule
        ? this.rule.fields.map(({ field, channel }) => {
          return {
            channel,
            field: field ? fields[`${field}`] : null
          }
        })
        : null
    },
    faciesColors () {
      return this.$store.getters.faciesTable
        .map(facies => {
          return {
            value: facies.code,
            color: facies.color,
          }
        })
    }
  },
}
</script>

<style scoped>

</style>

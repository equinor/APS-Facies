<template>
  <overlay-facies-table
    :value="value"
  />
</template>

<script>
import OverlayFaciesTable from './table'
import VueTypes from 'vue-types'
import { TruncationRule } from '@/store/utils/domain'

export default {
  components: {
    OverlayFaciesTable,
  },

  props: {
    value: VueTypes.instanceOf(TruncationRule).isRequired,
  },
}
</script>

<template>
  <overlay-facies-table
    :value="value"
  />
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

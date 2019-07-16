<template>
  <selection-table
    header-name="Zone"
    item-type="zone"
    show-name
    show-code
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import SelectionTable from '@/components/table/SelectionTable.vue'

@Component({
  components: {
    SelectionTable
  },
})
export default class ZoneSelection extends Vue {
}
</script>

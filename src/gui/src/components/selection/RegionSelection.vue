<template>
  <selection-table
    header-name="Region"
    item-type="region"
    no-data-text="A Zone must be selected, before its regions may be shown"
    show-code
    :show-name="showName"
    loading-text="Loading Regions"
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import SelectionTable from '@/components/table/SelectionTable.vue'

import { Region } from '@/utils/domain'

@Component({
  components: {
    SelectionTable
  },
})
export default class RegionSelection extends Vue {
  get regions (): Region[] { return this.$store.getters.regions }

  get showName (): boolean { return this.regions.some(region => !!region.name) }
}
</script>

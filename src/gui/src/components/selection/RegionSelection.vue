<template>
  <selection-table
    header-name="Region"
    item-type="region"
    no-data-text="A Zone must be selected, before its regions may be shown"
    show-name
    show-code
    loading-text="Loading Regions"
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
export default class RegionSelection extends Vue {
}
</script>

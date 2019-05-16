<template>
  <base-dropdown
    :items="available"
    :model-getter="getter"
    :model-setter="setter"
    label="Grid model"
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import BaseDropdown from '@/components/selection/dropdown/BaseDropdown.vue'

import { Store } from '@/store/typing'

type GridModel = string

@Component({
  components: {
    BaseDropdown,
  }
})
export default class ChooseGridModel extends Vue {
  get available () {
    return (this.$store as Store).state.gridModels.available
  }

  getter () {
    return (this.$store as Store).state.gridModels.current
  }
  async setter (value: GridModel) {
    await this.$store.dispatch('gridModels/select', value)
  }
}
</script>

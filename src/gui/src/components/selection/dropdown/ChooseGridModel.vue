<template>
  <base-dropdown
    :items="available"
    :model-getter="getter"
    :model-setter="setter"
    label="Grid model"
    :no-data-text="'No grids available'"
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
    return Object.values((this.$store as Store).state.gridModels.available)
      .map(grid => {
        return {
          text: grid.name,
          value: grid,
          disabled: !grid.exists,
        }
      })
  }

  getter () {
    const id = (this.$store as Store).state.gridModels.current
    return (this.$store as Store).state.gridModels.available[`${id}`]
  }
  async setter (value: GridModel) {
    await this.$store.dispatch('gridModels/select', value)
  }
}
</script>

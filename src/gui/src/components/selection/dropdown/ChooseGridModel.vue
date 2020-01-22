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
import { ListItem } from '@/utils/typing'
import GridModel from '@/utils/domain/gridModel'

@Component({
  components: {
    BaseDropdown,
  }
})
export default class ChooseGridModel extends Vue {
  get available (): ListItem<GridModel>[] {
    return Object.values((this.$store as Store).state.gridModels.available)
      .map(grid => {
        return {
          text: grid.name,
          value: grid,
          disabled: !grid.exists,
        }
      })
  }

  getter (): GridModel | undefined {
    const id = (this.$store as Store).state.gridModels.current
    return (this.$store as Store).state.gridModels.available[`${id}`]
  }

  async setter (value: GridModel): Promise<void> {
    await this.$store.dispatch('gridModels/select', value)
  }
}
</script>

<template>
  <base-dropdown
    v-model="gridModel"
    :items="available"
    label="Grid model"
    warn
    warn-message="This will remove all model specifications, including truncation rules, and Gaussian Random Fields for all zones, and regions."
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
          help: grid.hasDualIndexSystem ? 'Grid models with reverse staircase faults, <br/> are not yet supported in ERT mode' : '',
        }
      })
  }

  get gridModel (): GridModel | undefined {
    const id = (this.$store as Store).state.gridModels.current
    return (this.$store as Store).state.gridModels.available[`${id}`]
  }

  set gridModel (value: GridModel | undefined) {
    this.$store.dispatch('gridModels/select', value)
  }
}
</script>

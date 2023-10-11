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

<script setup lang="ts">
import BaseDropdown from '@/components/selection/dropdown/BaseDropdown.vue'

import { ListItem } from '@/utils/typing'
import GridModel from '@/utils/domain/gridModel'
import { useStore } from '../../../store'
import { computed } from 'vue'

const store = useStore()

const available = computed<ListItem<GridModel>[]>(() =>
  Object.values(store.state.gridModels.available).map((grid) => ({
      title: grid.name,
      value: grid,
      props: {
        disabled: !grid.exists,
        help: grid.hasDualIndexSystem
          ? 'Grid models with reverse staircase faults, <br/> are not yet supported in ERT mode'
          : '',
    }
  })),
)

const gridModel = computed({
  get: () => {
    const id = store.state.gridModels.current
    return id ? store.state.gridModels.available[id] : undefined
  },
  set: (value: GridModel | undefined) => {
    store.dispatch('gridModels/select', value)
  },
})
</script>

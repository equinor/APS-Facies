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
import { computed } from 'vue'
import { useGridModelStore } from '@/stores/grid-models'

const gridModelStore = useGridModelStore()

const available = computed<ListItem<GridModel>[]>(() =>
  (gridModelStore.available as GridModel[]).map((grid) => ({
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
  get: () => gridModelStore.current,
  set: (value: GridModel | null) => {
    if (!value) return
    gridModelStore.select(value)
  },
})
</script>

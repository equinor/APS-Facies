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

type GridModel = string

@Component({
  components: {
    BaseDropdown,
  }
})
export default class ChooseGridModel extends Vue {
  get available (): GridModel[] {
    return this.$store.state.gridModels.available
  }

  getter (): GridModel {
    return this.$store.state.gridModels.current
  }
  async setter (value: GridModel) {
    await this.$store.dispatch('gridModels/select', value)
  }
}
</script>

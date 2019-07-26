<template>
  <v-layout
    ma-0
    pa-0
    shrink
    align-center
    justify-center
  >
    <static-plot
      :data-definition="dataDefinition"
      :expand="expand"
    />
  </v-layout>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { TruncationRule } from '@/utils/domain'
import { Store } from '@/store/typing'

import StaticPlot from '@/components/plot/StaticPlot.vue'

function filterOnCode (data: number[][] | null, code: number) {
  if (!data) return []
  return data
    .map(arr => arr.map(val => val === code ? 1 : null))
}

@Component({
  components: {
    StaticPlot,
  },
})
export default class FaciesRealization extends Vue {
  data: number[][] | null = null

  @Prop({ required: true })
  readonly value!: TruncationRule

  @Prop({ default: false, type: Boolean })
  readonly expand!: boolean

  get faciesTable () { return (this.$store as Store).getters['facies/global/selected'] }
  get dataDefinition () {
    return this.faciesTable
      .map(({ color, code }) => {
        return {
          z: filterOnCode(this.data, code),
          zsmooth: 'best',
          type: 'heatmap',
          hoverinfo: 'none',
          colorscale: [[0, color], [1, color]],
          showscale: false,
        }
      })
  }

  @Watch('value.realization', { deep: true })
  onRealizationChanged (value: number[][] | null): void {
    this.data = value
  }
}
</script>

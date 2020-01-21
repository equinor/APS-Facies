<template>
  <v-row
    class="ma-0 pa-0 shrink"
    align="center"
    justify="center"
  >
    <static-plot
      v-tooltip.bottom="errorMessage"
      :data-definition="dataDefinition"
      :disabled="_disabled"
      :expand="expand"
    />
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { PlotData } from 'plotly.js'

import { GlobalFacies, TruncationRule } from '@/utils/domain'
import { Store } from '@/store/typing'

import StaticPlot from '@/components/plot/StaticPlot.vue'

function filterOnCode (data: number[][] | null, code: number): (1 | null)[][] {
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
  @Prop({ required: true })
  readonly value!: TruncationRule

  @Prop({ default: false, type: Boolean })
  readonly expand!: boolean

  @Prop({ default: false, type: Boolean })
  readonly disabled: boolean

  get faciesTable (): GlobalFacies[] { return (this.$store as Store).getters['facies/global/selected'] }

  get _disabled (): boolean { return this.disabled || !this.value.isRepresentative }

  get errorMessage (): string | undefined {
    return this._disabled
      ? 'The truncation rule has changed since it was simulated'
      : undefined
  }

  get dataDefinition (): Partial<PlotData>[] {
    return this.faciesTable
      .map(({ color, code }) => {
        return {
          z: filterOnCode(this.value.realization, code),
          zsmooth: 'best',
          type: 'heatmap',
          hoverinfo: 'none',
          colorscale: [[0, color], [1, color]],
          showscale: false,
        }
      })
  }
}
</script>

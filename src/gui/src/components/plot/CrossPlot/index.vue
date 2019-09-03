<template>
  <static-plot
    :data-definition="dataDefinition"
    :axis-names="{ x: field.name, y: other.name }"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { DEFAULT_POINT_SIZE } from '@/config'
import StaticPlot from '@/components/plot/StaticPlot.vue'
import { GaussianRandomField } from '@/utils/domain'

function flatten (arr: number[][] | null): number[] {
  // TODO: Should be superfluous when Array.prototype.flat is part of ECMAScript
  return arr
    ? arr.reduce((flat, a) => flat.concat(a))
    : []
}

@Component({
  components: {
    StaticPlot
  },
})
export default class CrossPlot extends Vue {
  @Prop({ required: true })
  readonly value: [GaussianRandomField, GaussianRandomField]

  get field () { return this.value[0] }
  get other () { return this.value[1] }

  get dataDefinition () {
    return this.field.simulated && this.other.simulated
      ? [{
        type: 'scattergl',
        mode: 'markers',
        marker: { size: DEFAULT_POINT_SIZE },
        // TODO: Use Array.prototype.flat when possible
        //       NOTE: Even though flat is part of ECMAScript now, RMS does not support it
        x: flatten(this.field.simulation),
        y: flatten(this.other.simulation),
      }]
      : []
  }
}
</script>

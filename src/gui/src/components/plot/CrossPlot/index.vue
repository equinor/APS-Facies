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
import { ID } from '@/utils/domain/types'

const flatten = (arr: number[][]) => {
  // TODO: Should be superfluous when Array.prototype.flat is part of ECMAScript
  return arr.reduce((flat, a) => flat.concat(a))
}

@Component({
  components: {
    StaticPlot
  },
})
export default class CrossPlot extends Vue {
  @Prop({ required: true })
  readonly value: GaussianRandomField | ID

  get field () { return this._getField(this.value[0]) }
  get other () { return this._getField(this.value[1]) }
  get dataDefinition () {
    return this.field.simulated && this.other.simulated
      ? [{
        type: 'scattergl',
        mode: 'markers',
        marker: { size: DEFAULT_POINT_SIZE },
        // TODO: Use Array.prototype.flat when possible
        //       NOTE: Even though flat is part of ECMAScript now, RMS does not support it
        x: flatten(this.field._data),
        y: flatten(this.other._data),
      }]
      : []
  }

  _getField (item: GaussianRandomField | ID) {
    return typeof item === 'string'
      ? this.$store.state.gaussianRandomFields.fields[`${item}`]
      : item
  }
}
</script>

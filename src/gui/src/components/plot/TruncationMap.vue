<template>
  <v-layout
    ma-0
    pa-0
    shrink
    align-center
    justify-center
  >
    <static-plot
      :data-definition="data.polygons"
      :annotations="data.annotations"
      :expand="expand"
      svg
    />
  </v-layout>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { TruncationRule } from '@/utils/domain'

import { makeTruncationRuleSpecification } from '@/utils'
import { plotify, PlotSpecification } from '@/utils/plotting'

@Component({
  // @ts-ignore
  asyncComputed: {
    data: {
      async get (): Promise<PlotSpecification> {
        return plotify(
          // @ts-ignore
          await rms.truncationPolygons(makeTruncationRuleSpecification(this.value, this.$store.getters)),
          // @ts-ignore
          this.selectedFacies
        )
      },
      shouldUpdate (): boolean {
        // @ts-ignore
        return this.canUpdate()
      },
      default () {
        return {
          polygons: [],
          annotations: null,
        }
      },
    },
  },

  components: {
    StaticPlot,
  },
})
export default class TruncationMap extends Vue {
  @Prop({ required: true })
  readonly value!: TruncationRule

  @Prop({ default: false, type: Boolean })
  readonly expand!: boolean

  get selectedFacies () {
    return this.$store.getters['facies/global/selected']
  }

  @Watch('selectedFacies', { deep: true })
  handler () {
    // To detect changes in alias
    if (this.canUpdate()) {
      // @ts-ignore
      this.$asyncComputed.data.update()
    }
  }

  canUpdate (): boolean {
    return this.$store.getters['truncationRules/ready'](this.value)
  }
}
</script>

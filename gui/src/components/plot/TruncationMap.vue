<template>
  <v-row
    class="ma-0 pa-0 shrink"
    align="center"
    justify="center"
  >
    <static-plot
      :data-definition="data.polygons"
      :annotations="data.annotations"
      :expand="expand"
      svg
    />
  </v-row>
</template>

<script lang="ts">
/* eslint-disable no-use-before-define */
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { TruncationRule } from '@/utils/domain'
import GlobalFacies from '@/utils/domain/facies/global'

import { makeTruncationRuleSpecification } from '@/utils'
import { plotify, PlotSpecification } from '@/utils/plotting'

@Component({
  asyncComputed: {
    data: {
      async get (): Promise<PlotSpecification> {
        return plotify(
          await rms.truncationPolygons(makeTruncationRuleSpecification((this as TruncationMap).value, this.$store.getters)),
          (this as TruncationMap).selectedFacies
        )
      },
      shouldUpdate (): boolean {
        return (this as TruncationMap).canUpdate()
      },
      default (): PlotSpecification {
        return {
          polygons: [],
          annotations: [],
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

  get selectedFacies (): GlobalFacies[] {
    return this.$store.getters['facies/global/selected']
  }

  @Watch('selectedFacies', { deep: true })
  handler (): void {
    // To detect changes in alias
    if (this.canUpdate()) {
      this.$asyncComputed.data.update()
    }
  }

  canUpdate (): boolean {
    return this.$store.getters['truncationRules/ready'](this.value)
  }
}
</script>
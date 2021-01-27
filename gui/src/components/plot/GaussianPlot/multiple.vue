<template>
  <v-container
    class="text-center ma-0 pa-0"
    fluid
  >
    <v-row
      class="xs12 pa-0 ma-0"
    >
      <v-row
        align="center"
        justify="center"
      >
        <v-col
          v-for="field in value"
          :key="field.id"
          :ref="`v-flex:${field.id}`"
          class="shrink"
        >
          <h5>{{ field.name }}</h5>
          <gaussian-plot
            v-if="field.simulated"
            pa-0
            ma-0
            :value="field"
            :size="size"
          />
          <v-progress-circular
            v-else
            :size="70"
            indeterminate
          />
        </v-col>
        <v-col
          cols="1"
          align-self="end"
        >
          <color-scale
            v-if="someSimulated"
          />
        </v-col>
      </v-row>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import GaussianPlot from './index.vue'
import ColorScale from '@/components/plot/ColorScale.vue'

import { GaussianRandomField } from '@/utils/domain'

import { DEFAULT_SIZE } from '@/config'

interface Size {
  max?: {
    width: number
    height: number
  }
  width: number
  height: number
}

@Component({
  components: {
    ColorScale,
    GaussianPlot,
  },
})
export default class MultipleGaussianPlots extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField[]

  size: Size = DEFAULT_SIZE

  get someSimulated (): boolean { return this.value.some(field => field.simulated) }

  @Watch('value')
  updateSimulation (fields: GaussianRandomField[]): void {
    if (this.$store.state.panels.preview.gaussianRandomFields) {
      this.$store.dispatch('gaussianRandomFields/updateSimulations', { fields })
    }
  }

  @Watch('content')
  handle (): void {
    this.$nextTick(() => {
      this.size = this.value
        .map(field => {
          if (Object.values(this.$refs).length > 0) {
            const el = this.$refs[`v-flex:${field.id}`][0].firstChild
            return {
              width: el.clientWidth,
              height: el.clientHeight,
            }
          } else {
            return DEFAULT_SIZE
          }
        })
        .reduce((max, curr) => {
          const air = 0.1
          return {
            width: Math.floor(Math.max(max.width, curr.width) * (1 - air)),
            height: Math.floor(Math.max(max.height, curr.height) * (1 - air)),
          }
        })
    })
  }
}
</script>

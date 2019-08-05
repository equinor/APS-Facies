<template>
  <v-container
    grid-list-md
    text-center
    ma-0
    pa-0
    fluid
  >
    <v-layout
      wrap
      xs12
      pa-0
      ma-0
    >
      <v-layout
        align-center
        justify-center
        wrap
      >
        <v-flex
          v-for="field in value"
          :key="field.id"
          :ref="`v-flex:${field.id}`"
          shrink
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
        </v-flex>
        <v-flex
          xs1
          align-self-end
        >
          <color-scale
            v-if="someSimulated"
          />
        </v-flex>
      </v-layout>
    </v-layout>
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
  updateSimulation (fields: GaussianRandomField[]) {
    if (this.$store.state.panels.preview.gaussianRandomFields) {
      this.$store.dispatch('gaussianRandomFields/updateSimulations', { fields })
    }
  }

  @Watch('content')
  handle () {
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

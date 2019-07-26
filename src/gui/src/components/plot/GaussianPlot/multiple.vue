<template>
  <v-container
    grid-list-md
    text-center
    ma-0
    pa-0
  >
    <v-layout
      wrap
      xs12
      pa-0
      ma-0
    >
      <v-flex
        v-for="(field, index) in value"
        :key="field.id"
        :ref="`v-flex:${field.id}`"
        column
      >
        <v-layout
          column
          align-center
        >
          <h5>{{ field.name }}</h5>
          <gaussian-plot
            pa-0
            ma-0
            :value="field"
            :size="size"
            :show-scale="index === (value.length - 1)"
          />
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import GaussianPlot from './index.vue'

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
    GaussianPlot,
  },
})
export default class MultipleGaussianPlots extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField[]

  size: Size = DEFAULT_SIZE

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

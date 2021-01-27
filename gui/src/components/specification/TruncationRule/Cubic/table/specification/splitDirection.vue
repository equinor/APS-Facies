<template>
  <v-radio-group
    v-model="splitDirection"
    label="Split direction"
  >
    <v-radio
      v-for="n in 2"
      :key="n"
      :label="labels[n - 1]"
      :value="n - 1"
    />
  </v-radio-group>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { Cubic } from '@/utils/domain'

@Component
export default class SplitDirection extends Vue {
  @Prop({ required: true })
  readonly value!: Cubic

  get splitDirection (): 1 | 0 { return this.value.direction.toInteger() }
  set splitDirection (value) { this.$store.dispatch('truncationRules/changeDirection', { rule: this.value, value }) }

  get labels (): { [_: number]: string } {
    return {
      0: 'Vertical',
      1: 'Horizontal',
    }
  }
}
</script>

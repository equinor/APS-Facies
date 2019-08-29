<template>
  <v-row
    align="center"
    justify="center"
    no-gutters
  >
    <v-col
      v-for="item in alphas"
      :key="item.channel"
      class="pa-0"
    >
      <alpha-selection
        :channel="item.channel"
        :value="item.selected"
        :rule="value"
        @input="val => update(item, val)"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { ID } from '@/utils/domain/types'
import TruncationRule from '@/utils/domain/truncationRule/base'
import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import { GaussianRandomField } from '@/utils/domain'
import { Store } from '@/store/typing'

import AlphaSelection from './AlphaSelection.vue'

function defaultChannels (num: number): { channel: number, selected: ID | '' }[] {
  const items = []
  for (let i = 1; i <= num; i++) {
    // NOTE: The alpha channels are (supposed to be) 1-indexed
    items.push({ channel: i, selected: '' })
  }
  return items
}

@Component({
  components: {
    AlphaSelection,
  },
})
export default class AlphaFields<
  T extends Polygon,
  S extends PolygonSerialization,
> extends Vue {
  @Prop({ required: true })
  readonly value!: TruncationRule<T, S>

  @Prop({ default: 2 })
  readonly minFields!: number

  get alphas () {
    return this.value
      ? this.value.backgroundFields
        .map((field, index) => {
          return {
            channel: index + 1,
            selected: field
          }
        })
      : defaultChannels(this.minFields)
  }

  update ({ channel }: { channel: number }, fieldId: ID | GaussianRandomField) {
    const field = fieldId
      ? (this.$store as Store).state.gaussianRandomFields.available[`${fieldId}`]
      : null
    return this.$store.dispatch('truncationRules/updateBackgroundField', {
      index: channel - 1,
      rule: this.value,
      field,
    })
  }
}
</script>

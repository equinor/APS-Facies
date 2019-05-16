<template>
  <v-layout>
    <v-flex
      v-for="item in alphas"
      :key="item.channel"
      pa-1
    >
      <alpha-selection
        :channel="item.channel"
        :value="item.selected"
        :rule="value"
        group=""
        @input="val => update(item, val)"
      />
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { ID } from '@/utils/domain/types'
import { TruncationRule } from '@/utils/domain'
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
export default class AlphaFields extends Vue {
  @Prop({ required: true })
  readonly value!: TruncationRule

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

  update ({ channel }: { channel: number }, fieldId: ID) {
    const field = (this.$store as Store).state.gaussianRandomFields.fields[`${fieldId}`]
    return this.$store.dispatch('truncationRules/updateBackgroundField', {
      index: channel - 1,
      rule: this.value,
      field: field || null
    })
  }
}
</script>

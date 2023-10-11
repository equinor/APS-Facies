<template>
  <v-row align="center" justify="center" no-gutters>
    <v-col v-for="item in alphas" :key="item.channel" class="pa-0">
      <alpha-selection
        :channel="item.channel"
        :value="item.selected"
        :rule="value"
        @input="(val: ID | null) => update(item, val)"
      />
    </v-col>
  </v-row>
</template>

<script
  setup
  lang="ts"
  generic="T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends TruncationRule<T, S, P>
"
>
import type { ID } from '@/utils/domain/types'
import type TruncationRule from '@/utils/domain/truncationRule/base'
import type {
  Polygon,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type { GaussianRandomField } from '@/utils/domain'

import AlphaSelection from './AlphaSelection.vue'
import { computed } from 'vue'
import { useTruncationRuleStore } from '@/stores/truncation-rules'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'

interface AlphaField {
  channel: number
  selected: GaussianRandomField | string | null
}

function defaultChannels(num: number): AlphaField[] {
  const items = []
  for (let i = 1; i <= num; i++) {
    // NOTE: The alpha channels are (supposed to be) 1-indexed
    items.push({ channel: i, selected: '' })
  }
  return items
}

type Props = {
  value: RULE
  minFields: number
}
const props = withDefaults(defineProps<Props>(), { minFields: 2 })
const fieldStore = useGaussianRandomFieldStore()
const ruleStore = useTruncationRuleStore()

const alphas = computed<AlphaField[]>(() =>
  props.value
    ? props.value.backgroundFields.map((field, index) => {
        return {
          channel: index + 1,
          selected: field,
        }
      })
    : defaultChannels(props.minFields),
)

async function update(
  { channel }: AlphaField,
  fieldId: ID | null,
): Promise<void> {
  const field = fieldId ? fieldStore.identifiedAvailable[fieldId] : null
  ruleStore.updateBackgroundField(props.value, channel - 1, field)
}
</script>

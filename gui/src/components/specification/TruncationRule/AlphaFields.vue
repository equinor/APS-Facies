<template>
  <v-row align="center" justify="center" no-gutters>
    <v-col v-for="item in alphas" :key="item.channel" class="pa-0">
      <alpha-selection
        :channel="item.channel"
        :value="item.selected"
        :rule="value"
        @input="(val: string | GaussianRandomField) => update(item, val)"
      />
    </v-col>
  </v-row>
</template>

<script
  setup
  lang="ts"
  generic="
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
"
>
import { ID } from '@/utils/domain/types'
import TruncationRule from '@/utils/domain/truncationRule/base'
import Polygon, {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import { GaussianRandomField } from '@/utils/domain'
import { Store } from '@/store/typing'

import AlphaSelection from './AlphaSelection.vue'
import { computed } from 'vue'
import { useStore } from '../../../store'

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
  value: TruncationRule<T, S, P>
  minFields: number
}
const props = withDefaults(defineProps<Props>(), { minFields: 2 })
const store = useStore()

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
  { channel }: { channel: number },
  fieldId: ID | GaussianRandomField,
): Promise<void> {
  const field = fieldId
    ? (store as Store).state.gaussianRandomFields.available[fieldId]
    : null
  await store.dispatch('truncationRules/updateBackgroundField', {
    index: channel - 1,
    rule: props.value,
    field,
  })
}
</script>

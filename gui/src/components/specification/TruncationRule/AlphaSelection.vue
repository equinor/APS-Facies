<template>
  <v-select v-model="selected" :items="fields" clearable variant="underlined">
    <template v-if="channel" slot="label">
      <span
        >α<sub>{{ channel }}</sub></span
      >
    </template>
  </v-select>
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
import type { GaussianRandomField } from '@/utils/domain'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import type TruncationRule from '@/utils/domain/truncationRule/base'
import type {
  Polygon,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type { ID } from '@/utils/domain/types'
import type { ListItem } from '@/utils/typing'
import { useStore } from '../../../store'
import { computed } from 'vue'

type Props = {
  value: GaussianRandomField | null
  rule: RULE
  channel?: number
  group?: ID | ''
}
const props = withDefaults(defineProps<Props>(), {
  channel: 0,
  group: '',
})
const store = useStore()
// why is `value: GaussianRandomField`, but the emit `input: ID`?
const emit = defineEmits<{
  (event: 'input', value: ID | null): void
}>()

const _fields = computed<GaussianRandomField[]>(() =>
  store.getters.fields.sort((a: GaussianRandomField, b: GaussianRandomField) =>
    a.name.localeCompare(b.name),
  ),
)

// TODO: Not used?
const id = computed<ID | ''>(() => props.value?.id ?? '')

const fields = computed<ListItem<string>[]>(() =>
  _fields.value.map((field) => {
    /* Is background field, and is not in the same location */
    let disabled = props.rule.isUsedInDifferentAlpha(field, props.channel)

    /* Are we dealing with a field used in overlay? */
    if (props.rule instanceof OverlayTruncationRule) {
      if (props.group) {
        if (props.rule.isUsedInBackground(field)) {
          /* A Gaussian Field used in overlay, CANNOT be used in the background, and vice versa */
          disabled = true
        } else {
          /* This field MAY be used in overlay */
          disabled =
            /* A Gaussian Field CANNOT be used twice in the same group */
            props.rule.isUsedInDifferentOverlayPolygon(props.group, field)
        }
      } else {
        /* This field MAY have been used in overlay */
        disabled = disabled || props.rule.isUsedInOverlay(field)
      }
    }
    if (props.value) {
      /* A field that is CURRENTLY selected, should never be disabled */
      disabled = disabled && props.value.id !== field.id
    }
    return {
      title: field.name,
      value: field.id,
      props: {
        disabled,
      },
    }
  }),
)
const selected = computed<ID | null>({
  get: () => {
    if (fields.value.some((item) => item.value === props.value?.id)) {
      return props.value?.id ?? null
    }
    return null
  },
  set: (value: ID | null) => emit('input', value),
})
</script>

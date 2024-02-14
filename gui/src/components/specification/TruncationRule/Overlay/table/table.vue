<template>
  <base-table
    :headers="headers"
    :items="polygons"
    :custom-sort="ordering"
    elevation="0"
    @input.stop
  >
    <template #item="{ item }">
      <tr>
        <td>
          <alpha-selection
            :value="item.field"
            :rule="rule"
            :group="item.group.id"
            hide-label
            @input="(field: string) => updateField(item, field)"
          />
        </td>
        <td>
          <overlay-facies-specification :value="item" :rule="rule" />
        </td>
        <td v-if="needFraction">
          <polygon-fraction-field :value="item" :rule="rule" />
        </td>
        <td>
          <fraction-field
            :model-value="item.center"
            @input="(val) => updateCenter(item, val)"
          />
        </td>
        <td>
          <polygon-order :value="item" :rule="rule" overlay />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script
  setup
  lang="ts"
  generic="T extends OverlayPolygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends OverlayTruncationRule<T, S, P> | InstantiatedOverlayTruncationRule
"
>
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import FractionField from '@/components/selection/FractionField.vue'
import PolygonFractionField from '@/components/selection/PolygonFractionField.vue'
import PolygonOrder from '@/components/specification/TruncationRule/order.vue'
import OverlayFaciesSpecification from '@/components/specification/Facies/overlay.vue'
import AlphaSelection from '@/components/specification/TruncationRule/AlphaSelection.vue'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type { InstantiatedOverlayTruncationRule } from '@/utils/domain'
import BaseTable from '@/components/baseComponents/BaseTable.vue'
import type OverlayPolygon from '@/utils/domain/polygon/overlay'
import type { ID } from '@/utils/domain/types'
import { Store } from '@/store/typing'
import type { HeaderItems } from '@/utils/typing'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { sortByOrder } from '@/utils'
import { computed } from 'vue'
import { useStore } from '../../../../../store'

type Props = {
  value: T[]
  rule: RULE
}
const props = defineProps<Props>()
const store = useStore()

const polygons = computed(() => props.value)

// TODO: Not used?
const fieldOptions = computed<{ value: ID; text: string; disabled: boolean }[]>(
  () =>
    Object.values((this.$store as Store).getters.fields).map((field) => {
      return {
        value: field.id,
        text: field.name,
        disabled: false,
      }
    }),
)

const needFraction = computed(() =>
  hasFaciesSpecifiedForMultiplePolygons(props.rule.overlayPolygons),
)

const headers = computed<HeaderItems>(() => [
  {
    text: 'GRF',
    value: 'field',
    help: 'Gaussian Random Field',
  },
  {
    text: 'Overlay Facies',
    value: 'facies',
  },
  ...(needFraction.value
    ? [
        {
          text: 'Probability Fraction',
          value: 'fraction',
        },
      ]
    : []),
  {
    text: 'Center',
    value: 'center',
    help: 'Truncation Interval Center Point',
    /* or: The overlay facies will look more continuous if the value of the center point of
    the truncation interval is 0 or 1 and look more fragmented if a value between 0 and 1,
    typically 0.5 is chosen. */
  },
  {
    text: 'Order',
    value: 'order',
  },
])

function ordering(
  items: OverlayPolygon[],
  index: number,
  isDescending: boolean,
): OverlayPolygon[] {
  return sortByOrder(items, index, isDescending)
}

async function updateField(
  polygon: OverlayPolygon,
  fieldId: ID,
): Promise<void> {
  const field = (store as Store).state.gaussianRandomFields.available[
    `${fieldId}`
  ]
  await store.dispatch('truncationRules/updateOverlayField', {
    rule: props.rule,
    polygon,
    field,
  })
}

async function updateCenter(
  polygon: OverlayPolygon,
  val: number,
): Promise<void> {
  await store.dispatch('truncationRules/updateOverlayCenter', {
    rule: props.rule,
    polygon,
    value: val,
  })
}
</script>

<style lang="scss" scoped>
th {
  white-space: normal;
  overflow-wrap: break-spaces;
}
</style>

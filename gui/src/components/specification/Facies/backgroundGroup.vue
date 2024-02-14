<template>
  <v-select
    :value="selected"
    :items="facies"
    multiple
    @input="(e: Facies[]) => update(e)"
  />
</template>

<script
  setup
  lang="ts"
  generic="T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends OverlayTruncationRule<T, S, P>
"
>
import type { Facies } from '@/utils/domain'
import type FaciesGroup from '@/utils/domain/facies/group'
import type {
  Polygon,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type { ID } from '@/utils/domain/types'
import type OverlayPolygon from '@/utils/domain/polygon/overlay'
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import type { ListItem } from '@/utils/typing'
import { computed } from 'vue'
import { useStore } from '../../../store'

function isFaciesSelected(
  group: FaciesGroup | undefined,
  facies: Facies,
): boolean {
  return group ? group.has(facies) : false
}

type Props = {
  value: { group: ID; polygons: OverlayPolygon[] }
  rule: RULE
}
const props = defineProps<Props>()
const store = useStore()

const group = computed(
  () => store.state.facies.groups.available[props.value.group],
)

const selected = computed(() => group.value?.facies ?? [])

const facies = computed<ListItem<Facies>[]>(() =>
  (Object.values(store.state.facies.available) as Facies[])
    .filter((facies) => facies.isChildOf(props.rule.parent))
    .map((facies) => {
      return {
        value: facies,
        title: facies.alias,
        props: {
          disabled:
            !isFaciesSelected(
              group.value,
              facies,
            ) /* I.e. the user should be allowed to DESELECT an already selected facies */ &&
            !store.getters['facies/availableForBackgroundFacies'](
              props.rule,
              facies,
            ),
        }
      }
    }),
)

async function update(facies: Facies[]): Promise<void> {
  if (!group.value) {
    const group = await store.dispatch('facies/groups/add', {
      facies,
      parent: props.rule.parent,
    })
    await store.dispatch('truncationRules/addPolygon', {
      rule: props.rule,
      group,
      overlay: true,
    })
  } else {
    await store.dispatch('facies/groups/update', {
      group: group.value,
      facies,
    })
  }
}
</script>

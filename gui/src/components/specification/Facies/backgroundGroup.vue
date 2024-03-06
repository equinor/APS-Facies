<template>
  <v-select
    :model-value="selected"
    :items="facies"
    multiple
    @update:model-value="(e: Facies[]) => update(e)"
    variant="underlined"
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
import { useFaciesGroupStore } from '@/stores/facies/groups'
import { useFaciesStore } from '@/stores/facies'
import { useTruncationRuleStore } from '@/stores/truncation-rules'

function isFaciesSelected(
  group: FaciesGroup | undefined,
  facies: Facies,
): boolean {
  return group ? group.has(facies) : false
}

type Props = {
  value: { id: ID; polygons: OverlayPolygon[] }
  rule: RULE
}
const props = defineProps<Props>()
const faciesStore = useFaciesStore()
const faciesGroupStore = useFaciesGroupStore()
const truncationRuleStore = useTruncationRuleStore()

const group = computed(
  () => faciesGroupStore.identifiedAvailable[props.value.id],
)

const selected = computed(() => group.value?.facies ?? [])

const facies = computed<ListItem<Facies>[]>(() =>
  (faciesStore.available as Facies[])
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
            !faciesStore.availableForBackgroundFacies(props.rule, facies),
        }
      }
    }),
)

function update(facies: Facies[]): void {
  if (!group.value) {
    const group = faciesGroupStore.add(facies, props.rule.parent)
    // When first creating an overlay group, the ID for the _currently_ opened dropdown menu
    // does not have its group ID refreshed
    truncationRuleStore.addPolygon(props.rule, { group, overlay: true })
  } else {
    if (facies.length === 0) {
      truncationRuleStore.removePolygon(props.rule, props.rule.polygons.find(polygon => 'group' in polygon && polygon.group.id === group.value.id)!)
    } else {
      faciesGroupStore.update(group.value, facies)
    }
  }
}
</script>

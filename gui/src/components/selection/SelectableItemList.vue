<template>
  <div class="d-flex flex-column ga-2">
    <v-progress-linear v-if="loading" indeterminate color="accent" />
    <p v-if="!loading && items.length === 0" class="text-caption">
      {{ noDataText }}
    </p>
    <div v-if="items.length > 0" role="list" class="d-flex flex-column ga-2">
      <selectable-item-card
        v-for="item in items"
        :key="item.id"
        role="listitem"
        :item="item"
        :name="nameOf(item)"
        :selected="item.selected"
        :is-current="item.id === currentId"
        @update:current="setCurrent"
        @toggle="toggle(item)"
      >
        <template v-if="showConformity" #settings>
          <conform-selection :value="item as Zone" />
        </template>
      </selectable-item-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import SelectableItemCard from '@/components/selection/SelectableItemCard.vue'
import ConformSelection from '@/components/selection/dropdown/ConformSelection.vue'

import { computed } from 'vue'
import type { ID } from '@/utils/domain/types'
import type { Region, Zone } from '@/utils/domain'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'
import { useFmuOptionStore } from '@/stores/fmu/options'

type Props = {
  itemType: 'zone' | 'region'
  noDataText?: string
  showName?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  noDataText: 'No data available',
  showName: false,
})

const zoneStore = useZoneStore()
const regionStore = useRegionStore()
const fmuOptionStore = useFmuOptionStore()

type GenericStore = {
  loading: boolean
  currentId: ID | null
  setCurrentId: (id: ID) => void
  select: (values: (Zone | Region)[]) => void
}

const store = computed(
  () =>
    (props.itemType === 'zone'
      ? zoneStore
      : regionStore) as unknown as GenericStore,
)

const loading = computed<boolean>(() => store.value.loading)
const currentId = computed(() => store.value.currentId)

const items = computed<(Zone | Region)[]>(() => {
  const available =
    props.itemType === 'zone'
      ? (zoneStore.available as Zone[])
      : (zoneStore.current?.regions ?? [])
  return [...available].sort((a, b) => a.code - b.code)
})

const typeName = computed(() => (props.itemType === 'zone' ? 'Zone' : 'Region'))

// An item named only by its number reads as 'Region 3', not as '3'
function nameOf(item: Zone | Region): string {
  const name = item.name?.trim()
  const isNamed = props.showName && !!name && !/^\d+$/.test(name)
  return isNamed ? name : `${typeName.value} ${item.code}`
}

const showConformity = computed(
  () => !!fmuOptionStore.fmuMode && props.itemType === 'zone',
)

function setCurrent(id: ID): void {
  store.value.setCurrentId(id)
}

// 'intermediate' counts as selected, so a click clears it
function toggle(item: Zone | Region): void {
  const selected = items.value.filter((candidate) =>
    candidate.id === item.id ? !item.selected : !!candidate.selected,
  )
  store.value.select(selected)
}
</script>

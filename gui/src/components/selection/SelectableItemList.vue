<template>
  <div class="d-flex flex-column ga-2">
    <v-progress-linear v-if="loading" indeterminate color="accent" />
    <p v-else-if="items.length === 0" class="text-caption">
      {{ noDataText }}
    </p>
    <div v-else role="list" class="d-flex flex-column ga-2">
      <selectable-item-card
        v-for="item in items"
        :key="item.id"
        role="listitem"
        :name="nameOf(item)"
        :code="item.code"
        :selected="item.selected"
        :is-current="item.id === currentId"
        @activate="setCurrent(item.id)"
        @toggle="toggle(item)"
      >
        <template #actions>
          <v-list-item
            prepend-icon="$copy"
            title="Copy"
            @click="copyPasteStore.copy(item)"
          />
          <v-list-item
            prepend-icon="$paste"
            title="Paste"
            :disabled="!canPaste(item) || !!copyPasteStore.isPasting(item)"
            @click="copyPasteStore.paste(item)"
          />
        </template>
        <template v-if="showConformity" #default>
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
import { useCopyPasteStore } from '@/stores/copy-paste'

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
const copyPasteStore = useCopyPasteStore()

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

function canPaste(item: Zone | Region): boolean {
  return !!copyPasteStore.source && copyPasteStore.source.id !== item.id
}

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

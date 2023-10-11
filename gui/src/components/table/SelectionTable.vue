<template>
  <base-selection-table
    v-model="selected"
    :headers="headers"
    :loading="loading"
    :loading-text="loadingText"
    :items="items"
    :no-data-text="_noDataText"
    v-model:current="currentId"
  >
    <template #item="{ item, isCurrent }: { item: T, isCurrent: boolean }">
      <td v-if="showName" class="text-start">
        {{ item.name }}
      </td>
      <td v-if="showCode" class="text-start">
        {{ item.code }}
      </td>
      <td v-if="showConformity" class="text-start">
        <conform-selection :value="item" :dark="isCurrent" />
      </td>
      <td>
        <v-row justify="center" align="center">
          <icon-button
            icon="copy"
            :color="isCurrent ? 'white' : undefined"
            @click="() => copy(item)"
          />
          <icon-button
            v-if="source"
            icon="paste"
            loading-spinner
            :disabled="!canPaste(item)"
            :waiting="isPasting(item)"
            @click="() => paste(item)"
          />
        </v-row>
      </td>
    </template>
  </base-selection-table>
</template>

<script
  setup
  lang="ts"
  generic="ItemType extends 'zone' | 'region', T extends ItemType extends 'zone' ? Zone : Region"
>
import BaseSelectionTable from '@/components/baseComponents/BaseSelectionTable.vue'
import IconButton from '@/components/selection/IconButton.vue'
import ConformSelection from '@/components/selection/dropdown/ConformSelection.vue'

import { computed } from 'vue'
import { HeaderItem } from '@/utils/typing'
import { ID } from '@/utils/domain/types'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'
import { Region, Zone } from '@/utils/domain'
import { useCopyPasteStore } from '@/stores/copy-paste'
import { useFmuOptionStore } from '@/stores/fmu/options'

type Props = {
  headerName: string
  itemType: 'zone' | 'region'
  noDataText?: string
  loadingText?: string
  showName?: boolean
  showCode?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  noDataText: '$vuetify.noDataText',
  loadingText: '$vuetify.dataIterator.loadingText',
  showName: false,
  showCode: false,
})
const zoneStore = useZoneStore()
const regionStore = useRegionStore()

type GenericStore = {
  loading: boolean
  currentId: ID | null
  setCurrentId: (id: ID) => void
  select: (values: T[]) => void
}

const store = computed(
  () =>
    (props.itemType === 'zone'
      ? zoneStore
      : regionStore) as unknown as GenericStore,
)

const loading = computed<boolean>(() => store.value.loading)
const _noDataText = computed(() =>
  loading.value ? `Loading ${props.itemType}s` : props.noDataText,
)

const headers = computed<HeaderItem[]>(() => [
  { text: 'Use', value: 'selected' },
  ...(props.showName ? [{ text: props.headerName, value: 'name' }] : []),
  ...(props.showCode ? [{ text: 'Code', sortable: true, value: 'code' }] : []),
  ...(showConformity.value
    ? [{ text: 'Conformity', value: 'conformity' }]
    : []),
  { text: 'Copy/Paste' },
])

const items = computed<T[]>(() => {
  switch (props.itemType) {
    case 'zone':
      return zoneStore.available as T[]
    case 'region':
      return (zoneStore.current?.regions as T[]) ?? []
  }
})

const currentId = computed({
  get: () => store.value.currentId ?? undefined,
  set: (value: ID | undefined) =>
    value ? store.value.setCurrentId(value) : null,
})

const selected = computed<T[]>({
  get: () => items.value.filter((item) => !!item.selected),
  set: (values: T[]) => {
    const filteredValues = items.value.filter((item) =>
      values.map(({ id }) => id).includes(item.id),
    )

    store.value.select(filteredValues)
  },
})

const copyPasteStore = useCopyPasteStore()
const fmuOptionStore = useFmuOptionStore()

const source = computed(() => copyPasteStore.source)
const showConformity = computed(
  () => fmuOptionStore.fmuMode && props.itemType === 'zone',
)

function canPaste(item: T): boolean {
  return source.value?.id !== item.id
}

function isPasting(item: T): boolean {
  return !!copyPasteStore.isPasting(item)
}

function copy(item: T): void {
  copyPasteStore.copy(item)
}

function paste(item: T): void {
  copyPasteStore.paste(item)
}
</script>

<style lang="scss" scoped>
div {
  flex-wrap: nowrap;
}
</style>

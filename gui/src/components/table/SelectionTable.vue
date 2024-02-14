<template>
  <base-selection-table
    v-model="selected"
    :headers="headers"
    :loading="loading"
    :loading-text="loadingText"
    :items="items"
    :no-data-text="_noDataText"
    v-model:current="current"
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

<script setup lang="ts" generic="T extends SelectableItem">
import BaseSelectionTable from '@/components/baseComponents/BaseSelectionTable.vue'
import IconButton from '@/components/selection/IconButton.vue'
import ConformSelection from '@/components/selection/dropdown/ConformSelection.vue'

import SelectableItem from '@/utils/domain/bases/selectableItem'

import { getId } from '@/utils'

import { useStore } from '../../store'
import { computed } from 'vue'
import { HeaderItem } from '../../utils/typing'
import { ID } from '../../utils/domain/types'

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
const store = useStore()

const loading = computed<boolean>(
  () => store.state[`${props.itemType}s`]._loading,
)
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

const items = computed<T[]>(() =>
  store.getters[`${props.itemType}s`].sort((a: T, b: T) => a.code - b.code),
)

// TODO: state.itemTypes.current is a string, which isn't T
const current = computed<ID | undefined>({
  get: () => store.state[`${props.itemType}s`].current,
  set: (value: ID | undefined) =>
    store.dispatch(`${props.itemType}s/current`, value),
})

const selected = computed<T[]>({
  get: () => items.value.filter((item) => !!item.selected),
  set: (values: T[]) => {
    const filteredValues = items.value.filter((item) =>
      values.map(({ id }) => id).includes(item.id),
    )
    store.dispatch(`${props.itemType}s/select`, filteredValues)
  },
})

// TODO: Typing doesn't like this.
const source = computed<T>(() => store.state.copyPaste.source)
const showConformity = computed(
  () => store.getters.fmuMode && props.itemType === 'zone',
)

function getItem(item: T): T | undefined {
  return items.value.find(({ id }) => id === item.id)
}

// TODO: not used?
function getColor(item: T): 'accent' | undefined {
  return getId(source.value) === item.id ? 'accent' : undefined
}

function canPaste(item: T): boolean {
  return source.value?.id !== item.id
}

function isPasting(item: T): boolean {
  return !!store.getters['copyPaste/isPasting'](getItem(item))
}

async function copy(item: T): Promise<void> {
  await store.dispatch('copyPaste/copy', getItem(item))
}

async function paste(item: T): Promise<void> {
  await store.dispatch('copyPaste/paste', getItem(item))
}

// TODO: not used?
function updateSelection(item: T, value: boolean): void {
  if (value) {
    selected.value = [...selected.value, item]
  } else {
    selected.value = selected.value.filter((el) => el.id !== item.id)
  }
}
</script>

<style lang="scss" scoped>
div {
  flex-wrap: nowrap;
}
</style>

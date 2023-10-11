<template>
  <v-data-table
    :value="value"
    :headers="_headers"
    :loading="loading"
    :loading-text="loadingText"
    :items="items"
    :no-data-text="noDataText"
    :custom-sort="customSort"
    :dense="dense"
    must-sort
    item-key="id"
    :class="`elevation-${elevation}`"
    :items-per-page="-1"
    hide-default-footer
    hide-default-header
  >
    <template #headers="{ columns }">
      <tr>
        <th v-for="column in columns" :key="column.title">
          <optional-help-item :value="column.title" />
        </th>
      </tr>
    </template>
    <template #item="{ item, isSelected, props }">
      <slot v-bind="props" :item="item" :isSelected="isSelected" name="item" />
    </template>
    <template #expanded-row="{ item, columns }">
      <slot :item="item" :columns="columns" name="expanded-item" />
    </template>
    <template #bottom> </template>
  </v-data-table>
</template>

<script setup lang="ts" generic="T extends Identifiable">
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'

import type { ID } from '@/utils/domain/types'
import type { HeaderItem, VuetifyColumns } from '@/utils/typing'
import { computed } from 'vue'
import type { Identifiable } from '@/utils/domain/bases/interfaces'

type Props = {
  value: T[]
  headers: HeaderItem[]
  items: T[]
  current?: ID
  expanded?: number[]
  loading?: boolean
  loadingText?: string
  noDataText?: string
  selectDisabled?: boolean
  selectError?: string
  elevation?: string
  customSort?: (
    items: T[],
    sortBy: string[],
    sortDesc: boolean[],
    locale: string,
    customSorters?: Record<string, (a: T, b: T) => number>,
  ) => T[]
  dense?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  current: undefined,
  expanded: () => [],
  loading: false,
  loadingText: '$vuetify.dataIterator.loadingText',
  noDataText: '$vuetify.noDataText',
  selectDisabled: false,
  type: Boolean,
  selectError: undefined,
  elevation: '1',
  customSort: undefined,
  dense: false,
})

defineSlots<{
  item(args: { item: T, props?: Props }): void
  'expanded-item'(args: { item: T, columns: VuetifyColumns }): void
}>()

const _headers = computed(() =>
  props.headers.map((header) => ({
    align: 'start' as 'start' | 'end' | 'center',
    sortable: false,
    title: header.text,
    value: header.value,
    ...header,
  })),
)
</script>

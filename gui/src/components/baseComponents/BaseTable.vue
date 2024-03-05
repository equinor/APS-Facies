<template>
  <v-data-table
    :headers="_headers"
    :loading="loading"
    :loading-text="loadingText"
    :expanded="_expanded"
    :items="items"
    :no-data-text="noDataText"
    :sort-by="sortBy"
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
          <span
            v-tooltip.botton="column.headerProps?.help"
          >
            {{ column.title }}
          </span>
        </th>
      </tr>
    </template>
    <template #item="{ item, props }">
      <slot v-bind="props" :item="item" name="item" />
    </template>
    <template #expanded-row="{ item, columns }">
      <slot :item="item" :columns="columns" name="expanded-item" />
    </template>
    <template #bottom> </template>
  </v-data-table>
</template>

<script setup lang="ts" generic="T extends Identifiable">
import type { ID } from '@/utils/domain/types'
import type { HeaderItem, VuetifyColumns } from '@/utils/typing'
import { computed } from 'vue'
import type { Identifiable } from '@/utils/domain/bases/interfaces'
import type { VDataTable } from 'vuetify/components'

type Props = {
  headers: HeaderItem[]
  items: T[]
  current?: ID
  expanded?: T[]
  loading?: boolean
  loadingText?: string
  noDataText?: string
  selectDisabled?: boolean
  selectError?: string
  elevation?: string
  sortBy?: VDataTable['sortBy']
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
  sortBy: undefined,
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

const _expanded = computed<ID[]>(() => props.expanded.map((item) => item.id))
</script>

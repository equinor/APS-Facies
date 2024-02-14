<template>
  <base-table
    :value="modelValue"
    :headers="headers"
    :loading="loading"
    :loading-text="loadingText"
    :items="items"
    :no-data-text="noDataText"
    :expanded="props.expanded"
  >
    <template #item="{ item }: { item: T }">
      <tr
        :class="isCurrent(item) ? 'font-weight-bold' : ''"
        :style="isCurrent(item) ? currentStyle : ''"
        @click="() => propagateCurrent(item)"
      >
        <td>
          <floating-tooltip
            :disabled="!selectDisabled"
            :triggers="['hover']"
            style="flex-shrink: 1"
          >
            <v-checkbox
              :style="{ marginTop: 0 }"
              :model-value="isSelected(item)"
              :indeterminate="isIndeterminate(item)"
              :disabled="selectDisabled"
              :color="isCurrent(item) ? 'white' : undefined"
              primary
              hide-details
              @click.passive.stop="toggleSelection(item)"
            />
            <template #popper>{{ selectError }}</template>
          </floating-tooltip>
        </td>
        <slot
          :item="item"
          :is-selected="isSelected(item)"
          :is-current="isCurrent(item)"
          name="item"
        />
      </tr>
    </template>
    <template #expanded-item="{ item, columns }">
      <slot :item="item" :columns="columns" name="expanded-item" />
    </template>
  </base-table>
</template>

<script setup lang="ts" generic="T extends Identifiable">
import BaseTable from '@/components/baseComponents/BaseTable.vue'
import SelectableItem from '@/utils/domain/bases/selectableItem'
import type { ID } from '@/utils/domain/types'
import { computed } from 'vue'
import { useTheme } from 'vuetify'
import type { HeaderItem, VuetifyColumns } from '@/utils/typing'
import type { Identifiable } from '@/utils/domain/bases/interfaces'

const props = withDefaults(defineProps<{
  modelValue: T[]
  headers: HeaderItem[]
  items: T[]
  current?: ID | null
  expanded?: T[]
  loading?: boolean
  loadingText?: string
  noDataText?: string
  selectDisabled?: boolean
  selectError?: string
}>(), {
  current: undefined,
  expanded: () => [],
  loading: false,
  loadingText: '$vuetify.dataIterator.loadingText',
  noDataText: '$vuetify.noDataText',
  selectDisabled: false,
  type: Boolean,
  selectError: undefined,
})

const emit = defineEmits<{
  (event: 'update:model-value', value: T[]): void
  (event: 'update:current', value: ID): void
  (event: 'update:expanded', value: T[]): void
}>()

defineSlots<{
  item(props: { item: T, isSelected: boolean, isCurrent: boolean }): void
  'expanded-item'(props: { item: T, columns: VuetifyColumns }): void
}>()

const theme = useTheme()
const currentStyle = computed(() => {
  return {
    background: theme.global.current.value.colors.primary,
    color: 'white',
  }
})

function isCurrent(item: T): boolean {
  if (!props.current) return false
  return item.id === props.current
}

const isSelected = computed(() => {
  return (item: T) => props.modelValue.includes(item)
})

function propagateCurrent(item: T): void {
  emit('update:current', item.id!)
}

function toggleSelection(item: T): void {
  const value = !isSelected.value(item)
  if (value) {
    emit('update:model-value', [...props.modelValue, item])
  } else {
    emit(
      'update:model-value',
      props.modelValue.filter((el) => el.id !== item.id),
    )
  }
}

function isIndeterminate(item: T): boolean {
  return item instanceof SelectableItem
    ? item.selected === 'intermediate'
    : false
}
</script>

<style scoped>
td,
:deep(td) {
  background: unset;
}
</style>

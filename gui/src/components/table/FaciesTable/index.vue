<template>
  <base-selection-table
    v-model="selected"
    :current="currentId"
    :items="facies as GlobalFacies[]"
    :expanded="expanded"
    :headers="headers"
    :loading="loading"
    :loading-text="'Loading Facies from RMS'"
    :no-data-text="noDataText"
    :select-disabled="!canSelect"
    :select-error="selectFaciesError"
    @update:current="(value) => (currentId = value)"
  >
    <template #item="{ item }">
      <facies-row
        :mode-value="item as GlobalFacies"
        :expanded="expanded as GlobalFacies[]"
        @expanded="(items) => (expanded = items)"
      />
    </template>
    <template #expanded-item="{ item, columns }">
      <tr>
        <td :colspan="columns.length">
          <color-picker
            :model-value="item.color"
            :colors="availableColors"
            @update:model-value="(color) => (item.color = color)"
          />
        </td>
      </tr>
    </template>
  </base-selection-table>
</template>

<script setup lang="ts">
import BaseSelectionTable from '@/components/baseComponents/BaseSelectionTable.vue'
import ColorPicker from '@/components/ColorPicker.vue'
import FaciesRow from '@/components/table/FaciesTable/FaciesRow.vue'

import type { Facies, GlobalFacies } from '@/utils/domain'

import { hasCurrentParents } from '@/utils'
import { ref, computed } from 'vue'
import { useRegionStore } from '@/stores/regions'
import { useRootStore } from '@/stores'
import { useGlobalFaciesStore } from '@/stores/facies/global'
import { useFaciesStore } from '@/stores/facies'
import { useConstantsFaciesColorsStore } from '@/stores/constants/facies-colors'
import type { ID } from '@/utils/domain/types'

const props = withDefaults(defineProps<{ hideAlias: boolean }>(), {
  hideAlias: false,
})

const expanded = ref<GlobalFacies[]>([])

const regionStore = useRegionStore()
const rootStore = useRootStore()
const faciesStore = useFaciesStore()
const faciesGlobalStore = useGlobalFaciesStore()
const colorStore = useConstantsFaciesColorsStore()

const canSelect = computed<boolean>(() => rootStore.canSpecifyModelSettings)
const loading = computed<boolean>(() => faciesGlobalStore.loading)

const currentId = computed({
  get: () => faciesGlobalStore.currentId,
  set: (id: ID | null) => faciesGlobalStore.setCurrentId(id),
})

const noDataText = computed(() =>
  loading.value
    ? 'Loading facies table from RMS'
    : 'There are no facies for the selected well logs. You may still add new facies.',
)

const facies = computed<GlobalFacies[]>(() =>
  [...(faciesGlobalStore.available as GlobalFacies[])].sort(
    (a, b) => a.code - b.code,
  ),
)
const parent = computed(() => rootStore.parent)

const headers = computed(() => [
  {
    text: 'Use',
    value: 'selected',
  },
  {
    text: 'Notes',
    value: '',
  },
  {
    text: 'Facies',
    value: 'name',
  },
  ...(props.hideAlias
    ? []
    : [
        {
          text: 'Alias',
          value: 'alias',
        },
      ]),
  {
    text: 'Code',
    sortable: true,
    value: 'code',
  },
  {
    text: 'Color',
    value: 'color',
  },
])

const selected = computed<GlobalFacies[]>({
  get: () => {
    return (faciesGlobalStore.available as GlobalFacies[]).filter(
      (globalFacies) =>
        (faciesStore.available as Facies[]).some(
          (localFacies: Facies) =>
            hasCurrentParents(localFacies) &&
            localFacies.facies.id === globalFacies.id,
        ),
    ) as GlobalFacies[]
  },
  set: (value: GlobalFacies[]) => faciesStore.select(value, parent.value),
})

const selectFaciesError = computed(() => {
  if (canSelect.value) return ''
  const item = regionStore.use && !parent.value.region ? 'Region' : 'Zone'
  return `A ${item} must be selected, before including a facies in the model`
})

const availableColors = computed(() => colorStore.current?.colors ?? [])
</script>

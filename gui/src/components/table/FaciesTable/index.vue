<template>
  <base-selection-table
    :items="(facies as GlobalFacies[])"
    v-model:current="currentId"
    v-model:expanded="expanded"
    v-model="selected"
    :headers="headers"
    :loading="loading"
    :loading-text="'Loading Facies from RMS'"
    :no-data-text="noDataText"
    :select-disabled="!canSelect"
    :select-error="selectFaciesError"
  >
    <template #item="{ item: facies }">
      <td class="dense">
        <informational-icons :value="facies" :current="currentId" />
      </td>
      <td class="text-left">
        <span v-if="isFaciesFromRms(facies)">
          {{ facies.name }}
        </span>
        <editable-cell
          v-else
          :value="facies"
          field="name"
          @submit="changeName"
        />
      </td>
      <td v-if="!hideAlias" class="text-left">
        <editable-cell :value="facies" field="alias" @submit="changeAlias" />
      </td>
      <td class="text-left">
        <span v-if="isFaciesFromRms(facies)">
          {{ facies.code }}
        </span>
        <editable-cell
          v-else
          :value="facies"
          :restrictions="faciesCodeRestrictions(facies)"
          field="code"
          numeric
          @submit="changeCode"
        />
      </td>
      <td
        :style="{ backgroundColor: facies.color, cursor: 'pointer' }"
        @click.stop="() => changeColorSelection(facies)"
      />
    </template>
    <template #expanded-item="{ item, columns }">
      <tr>
        <td :colspan="columns.length">
          <color-picker
            :model-value="item.color"
            :colors="availableColors"
            @update:model-value="(color) => item.color = color"
          />
        </td>
      </tr>
    </template>
  </base-selection-table>
</template>

<script setup lang="ts">
import EditableCell from '@/components/table/EditableCell.vue'
import BaseSelectionTable from '@/components/baseComponents/BaseSelectionTable.vue'
import ColorPicker from '@/components/ColorPicker.vue'
import InformationalIcons from '@/components/table/FaciesTable/InformationalIcons.vue'

import type { Facies, GlobalFacies } from '@/utils/domain'

import { hasCurrentParents } from '@/utils'
import { ref, computed } from 'vue'
import { useRegionStore } from '@/stores/regions'
import { useRootStore } from '@/stores'
import { useFaciesGlobalStore } from '@/stores/facies/global'
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
const faciesGlobalStore = useFaciesGlobalStore()
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
  [...faciesGlobalStore.available as GlobalFacies[]].sort((a, b) => a.code - b.code)
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
    return (faciesGlobalStore.available as GlobalFacies[]).filter((globalFacies) =>
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

function isFaciesFromRms(facies: GlobalFacies): boolean {
  return faciesStore.isFromRMS(facies)
}

function faciesCodeRestrictions(
  globalFacies: GlobalFacies,
): ((code: string) => string)[] {
  return [
    (code: string): string => (!code ? 'A code cannot be empty' : ''),
    (code): string => {
      try {
        Number.parseInt(code, 10)
        return ''
      } catch {
        return 'Code must be an integer'
      }
    },
    (code: string): string =>
      Number.parseInt(code, 10) < 0 ? 'Code must be non-negative' : '',
    (code: string): string =>
      facies.value
        .filter(({ id }) => globalFacies.id !== id)
        .map(({ code }) => code.toString(10))
        .includes(code)
        ? 'Code is used by a different Facies'
        : '',
  ]
}

const availableColors = computed(
  () => colorStore.current?.colors ?? [],
)

async function changeName(facies: GlobalFacies): Promise<void> {
  faciesGlobalStore.changeName(facies.id, facies.name || `F${facies.code}`)
}

async function changeAlias(facies: GlobalFacies): Promise<void> {
  faciesGlobalStore.changeAlias(facies.id, facies.alias)
}

async function changeCode(facies: GlobalFacies): Promise<void> {
  faciesGlobalStore.changeCode(facies.id, facies.code)
}

function changeColorSelection(facies: GlobalFacies): void {
  const previous = expanded.value.pop()
  if (previous && previous.id === facies.id) {
    expanded.value = []
  } else {
    expanded.value = [facies]
  }
}
</script>

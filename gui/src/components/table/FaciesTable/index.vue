<template>
  <base-selection-table
    v-model="selected"
    :headers="headers"
    :loading="loading"
    :loading-text="'Loading Facies from RMS'"
    :current.sync="current"
    :no-data-text="noDataText"
    :items="facies"
    :expanded="expanded"
    :select-disabled="!canSelect"
    :select-error="selectFaciesError"
  >
    <template #item="{ item: facies }">
      <td class="dense">
        <informational-icons :value="facies" :current="current" />
      </td>
      <td class="text-left">
        <editable-cell
          v-if="!isFaciesFromRms(facies)"
          :value="facies"
          field="name"
          @submit="changeName"
        />
        <span v-else>
          {{ facies.name }}
        </span>
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
        :style="{ backgroundColor: facies.color }"
        @click.stop="() => changeColorSelection(facies)"
      />
    </template>
    <template #expanded-item="{ item, headers }">
      <td :colspan="headers.length">
        <v-swatches
          :value="item.color"
          :swatches="availableColors"
          inline
          swatches-size="30"
          @input="(color) => changeColor(item, color)"
        />
      </td>
    </template>
  </base-selection-table>
</template>

<script setup lang="ts">
import VSwatches from 'vue-swatches'
import EditableCell from '@/components/table/EditableCell.vue'
import BaseSelectionTable from '@/components/baseComponents/BaseSelectionTable.vue'
import InformationalIcons from '@/components/table/FaciesTable/InformationalIcons.vue'

import { Facies, GlobalFacies } from '@/utils/domain'

import { hasCurrentParents } from '@/utils'
import { ref, computed } from 'vue'
import { useStore } from '../../../store'

const props = withDefaults(defineProps<{ hideAlias: boolean }>(), {
  hideAlias: false,
})
const store = useStore()

const expanded = ref<Facies[]>([])

// TODO: Typing is wrong.
const canSelect = computed<boolean>(() => store.getters.canSpecifyModelSettings)
// TODO: Typing is wrong.
const loading = computed<boolean>(() => store.state.facies.global._loading)

// TODO: The typing of store.state.facies.global.current is probably wrong,
// or this usage is wrong. Gonna have to fix that.
const current = computed({
  get: () => store.state.facies.global.current as GlobalFacies,
  set: ({ id }: GlobalFacies) =>
    store.dispatch('facies/global/current', { id }),
})

const noDataText = computed(() =>
  loading.value
    ? 'Loading facies table from RMS'
    : 'There are no facies for the selected well logs. You may still add new facies.',
)

const facies = computed(() => store.getters.faciesTable)
const parent = computed(() => store.getters.parent)

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

const selected = computed({
  get: () =>
    Object.values(store.state.facies.global.available).filter(
      (globalFacies) =>
        Object.values(store.state.facies.available)
          .filter((localFacies) =>
            hasCurrentParents(localFacies, store.getters),
          )
          .findIndex(
            (localFacies) => localFacies.facies.id === globalFacies.id,
          ) >= 0,
    ),
  set: (value: GlobalFacies[]) =>
    store.dispatch('facies/select', {
      items: value,
      parent: parent.value,
    }),
})

const availableColors = computed(
  () => store.getters['constants/faciesColors/available'],
)

const selectFaciesError = computed(() => {
  const item =
    store.state.regions.use && !parent.value.region ? 'Region' : 'Zone'
  return !canSelect.value
    ? `A ${item} must be selected, before including a facies in the model`
    : ''
})

// TODO: unused?
const blockedWellLogParameter = computed(
  () => store.getters.blockedWellLogParameter,
)

function isFaciesFromRms(facies: GlobalFacies): boolean {
  return store.getters['facies/isFromRMS'](facies)
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

async function changeColor(facies: GlobalFacies, color: string): Promise<void> {
  if (facies.color !== color) {
    // Only dispatch when the color *actually* changes
    await store.dispatch('facies/global/changeColor', {
      id: facies.id,
      color,
    })
  }
}

async function changeName(facies: GlobalFacies): Promise<void> {
  await store.dispatch('facies/global/changeName', {
    id: facies.id,
    name: facies.name || `F${facies.code}`,
  })
}

async function changeAlias(facies: GlobalFacies): Promise<void> {
  await store.dispatch('facies/global/changeAlias', facies)
}

async function changeCode(facies: GlobalFacies): Promise<void> {
  await store.dispatch('facies/global/changeCode', facies)
}

function changeColorSelection(facies: Facies): void {
  const previous = expanded.value.pop()
  if (previous && previous.id === facies.id) {
    expanded.value = []
  } else {
    expanded.value = [facies]
  }
}
</script>

<template>
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
      @submit="name => facies.name = name.toString() || `F${facies.code}`"
    />
  </td>
  <td v-if="!hideAlias" class="text-left">
    <editable-cell
      :value="facies"
      field="alias"
      @submit="(alias) => facies.alias = alias.toString()"
    />
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
      @submit="code => facies.code = typeof code === 'number' ? code : parseInt(code, 10)"
    />
  </td>
  <td
    :style="{ backgroundColor: facies.color, cursor: 'pointer' }"
    @click.stop="() => changeColorSelection(facies)"
  />
</template>

<script setup lang="ts">
import EditableCell from '@/components/table/EditableCell.vue'
import InformationalIcons from '@/components/table/FaciesTable/InformationalIcons.vue'

import { type GlobalFacies } from '@/utils/domain'

import { computed } from 'vue'
import { useFaciesGlobalStore } from '@/stores/facies/global'
import { useFaciesStore } from '@/stores/facies'
import type { ID } from '@/utils/domain/types'

const props = withDefaults(defineProps<{
  modeValue: GlobalFacies
  expanded?: GlobalFacies[]
  hideAlias?: boolean
}>(), {
  hideAlias: false,
})

const emit = defineEmits<{
  (event: 'update:modelValue', value: GlobalFacies): void
  (event: 'expanded', value: GlobalFacies[]) :void
}>()

const facies = computed(() => props.modeValue)

const faciesStore = useFaciesStore()
const faciesGlobalStore = useFaciesGlobalStore()


const currentId = computed({
  get: () => faciesGlobalStore.currentId,
  set: (id: ID | null) => faciesGlobalStore.setCurrentId(id),
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
      faciesGlobalStore.available
        .filter(({ id }) => globalFacies.id !== id)
        .map(({ code }) => code.toString(10))
        .includes(code)
        ? 'Code is used by a different Facies'
        : '',
  ]
}

function changeColorSelection(facies: GlobalFacies): void {
  const exists = props.expanded?.find(({ id }) => facies.id === id)
  if (exists) {
    emit('expanded', [])
  } else {
    emit('expanded', [facies])
  }
}
</script>

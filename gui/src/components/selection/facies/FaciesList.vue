<template>
  <div class="d-flex flex-column ga-2">
    <v-progress-linear v-if="loading" indeterminate color="accent" />
    <p v-else-if="facies.length === 0" class="text-caption">
      There are no facies for the selected well logs. You may still add new
      facies.
    </p>
    <template v-else>
      <p v-if="!canSelect" class="text-caption">
        {{ selectFaciesError }}
      </p>
      <div role="list" class="d-flex flex-column ga-2">
        <selectable-item-card
          v-for="item in facies"
          :key="item.id"
          role="listitem"
          :name="item.name"
          :code="item.code"
          :selected="isSelected(item)"
          :is-current="item.id === currentId"
          :select-disabled="!canSelect"
          @activate="faciesGlobalStore.setCurrentId(item.id)"
          @toggle="toggle(item)"
        >
          <template #prepend>
            <v-btn
              :color="item.color"
              :aria-label="`Change the colour of ${item.name}`"
              :aria-expanded="expandedId === item.id"
              icon
              variant="flat"
              size="x-small"
              rounded="lg"
              @click.stop="toggleColors(item)"
            />
          </template>
          <template #actions>
            <v-list-item
              prepend-icon="$remove"
              title="Delete"
              :subtitle="
                isFromRms(item) ? 'From RMS, and cannot be deleted' : undefined
              "
              :disabled="isFromRms(item)"
              @click="remove(item)"
            />
          </template>
          <facies-details :facies="item" />
          <color-picker
            v-if="expandedId === item.id"
            :model-value="item.color"
            :colors="availableColors"
            @update:model-value="(color) => (item.color = color)"
          />
        </selectable-item-card>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import SelectableItemCard from '@/components/selection/SelectableItemCard.vue'
import FaciesDetails from '@/components/selection/facies/FaciesDetails.vue'
import ColorPicker from '@/components/ColorPicker.vue'

import type { Facies, GlobalFacies } from '@/utils/domain'
import type { ID } from '@/utils/domain/types'

import { hasCurrentParents } from '@/utils'
import { computed, ref } from 'vue'
import { useRegionStore } from '@/stores/regions'
import { useRootStore } from '@/stores'
import { useGlobalFaciesStore } from '@/stores/facies/global'
import { useFaciesStore } from '@/stores/facies'
import { useConstantsFaciesColorsStore } from '@/stores/constants/facies-colors'

const regionStore = useRegionStore()
const rootStore = useRootStore()
const faciesStore = useFaciesStore()
const faciesGlobalStore = useGlobalFaciesStore()
const colorStore = useConstantsFaciesColorsStore()

const canSelect = computed<boolean>(() => rootStore.canSpecifyModelSettings)
const loading = computed<boolean>(() => faciesGlobalStore.loading)
const currentId = computed(() => faciesGlobalStore.currentId)

const facies = computed<GlobalFacies[]>(() =>
  [...(faciesGlobalStore.available as GlobalFacies[])].sort(
    (a, b) => a.code - b.code,
  ),
)
const parent = computed(() => rootStore.parent)

const selected = computed<GlobalFacies[]>(() =>
  (faciesGlobalStore.available as GlobalFacies[]).filter((globalFacies) =>
    (faciesStore.available as Facies[]).some(
      (localFacies: Facies) =>
        hasCurrentParents(localFacies) &&
        localFacies.facies.id === globalFacies.id,
    ),
  ),
)

const selectFaciesError = computed(() => {
  const item = regionStore.use && !parent.value.region ? 'Region' : 'Zone'
  return `A ${item} must be selected, before including a facies in the model`
})

const availableColors = computed(() => colorStore.current?.colors ?? [])

const expandedId = ref<ID | null>(null)

function isSelected(item: GlobalFacies): boolean {
  return selected.value.includes(item)
}

function isFromRms(item: GlobalFacies): boolean {
  return faciesStore.isFromRMS(item)
}

function toggle(item: GlobalFacies): void {
  faciesStore.select(
    isSelected(item)
      ? selected.value.filter(({ id }) => id !== item.id)
      : [...selected.value, item],
    parent.value,
  )
}

function toggleColors(item: GlobalFacies): void {
  expandedId.value = expandedId.value === item.id ? null : item.id
}

function remove(item: GlobalFacies): void {
  faciesGlobalStore.removeAvailable(item)
  if (currentId.value === item.id) faciesGlobalStore.setCurrentId(null)
}
</script>

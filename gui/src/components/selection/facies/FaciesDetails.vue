<template>
  <div class="facies-details d-flex flex-column ga-1">
    <template v-if="!isFromRms">
      <labeled-field label="Name" position="start">
        <template #default="{ fieldAttrs }">
          <editable-cell
            v-bind="fieldAttrs"
            :value="facies"
            field="name"
            @submit="
              (name) => (facies.name = name.toString() || `F${facies.code}`)
            "
          />
        </template>
      </labeled-field>
      <labeled-field label="Code" position="start">
        <template #default="{ fieldAttrs }">
          <editable-cell
            v-bind="fieldAttrs"
            :value="facies"
            :restrictions="codeRestrictions"
            field="code"
            numeric
            @submit="
              (code) =>
                (facies.code =
                  typeof code === 'number' ? code : parseInt(code, 10))
            "
          />
        </template>
      </labeled-field>
    </template>
    <div class="d-flex align-center ga-3">
      <labeled-field label="Alias" position="start" class="flex-grow-1">
        <template #default="{ fieldAttrs }">
          <editable-cell
            v-bind="fieldAttrs"
            :value="facies"
            field="alias"
            @submit="(alias) => (facies.alias = alias.toString())"
          />
        </template>
      </labeled-field>
      <informational-icons :value="facies" />
    </div>
  </div>
</template>

<script setup lang="ts">
import EditableCell from '@/components/table/EditableCell.vue'
import LabeledField from '@/components/baseComponents/LabeledField.vue'
import InformationalIcons from '@/components/selection/facies/InformationalIcons.vue'

import type { GlobalFacies } from '@/utils/domain'
import { computed } from 'vue'
import { useFaciesStore } from '@/stores/facies'
import { useGlobalFaciesStore } from '@/stores/facies/global'

const props = defineProps<{ facies: GlobalFacies }>()

const faciesStore = useFaciesStore()
const faciesGlobalStore = useGlobalFaciesStore()

const isFromRms = computed(() => faciesStore.isFromRMS(props.facies))

const codeRestrictions: ((code: string) => string)[] = [
  (code) => (code === '' ? 'A code cannot be empty' : ''),
  (code) =>
    Number.isInteger(Number(code)) ? '' : 'Code must be a whole number',
  (code) => (Number(code) < 0 ? 'Code must be non-negative' : ''),
  (code) =>
    faciesGlobalStore.available.some(
      ({ id, code: other }) => id !== props.facies.id && other === Number(code),
    )
      ? 'Code is used by a different Facies'
      : '',
]
</script>

<style lang="scss" scoped>
.facies-details :deep(.v-label) {
  min-width: 3.5rem;
}
</style>

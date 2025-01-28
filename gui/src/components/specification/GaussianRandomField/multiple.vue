<template>
  <v-expansion-panel value="gaussianRandomFields" elevation="0">
    <v-expansion-panel-title v-slot="{ expanded }">
      <v-row class="pa-0 ma-0" justify="center" align="center">
        <v-col>
          <section-title>Gaussian Random Fields (GRF)</section-title>
        </v-col>
        <v-col v-show="expanded" cols="2">
          <icon-button icon="add" @click="addField" />
        </v-col>
      </v-row>
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <cross-section />
      <v-expansion-panels v-model="panels" variant="accordion" multiple>
        <v-expansion-panel
          v-for="field in fields"
          :key="field.id"
          elevation="0"
        >
          <template #title>
            <v-row class="fill-height" align="center" justify="start">
              <v-col cols="4">
                <gaussian-field-name :ref="field.id" :value="field" />
              </v-col>
              <v-col cols="1">
                <icon-button icon="remove" @click.stop="deleteField(field)" />
                <confirmation-dialog ref="deleteDialogRefs" />
              </v-col>
            </v-row>
          </template>
          <template #text>
            <gaussian-random-field :value="field" />
          </template>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup lang="ts">
import GaussianRandomField from '@/components/specification/GaussianRandomField/index.vue'
import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog.vue'
import GaussianFieldName from '@/components/specification/GaussianRandomField/GaussianFieldName.vue'
import IconButton from '@/components/selection/IconButton.vue'
import CrossSection from '@/components/specification/GaussianRandomField/CrossSection.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'

import type { GaussianRandomField as Field } from '@/utils/domain'
import { computed, ref } from 'vue'
import { usePanelStore } from '@/stores/panels'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'

const panelStore = usePanelStore()
const fieldStore = useGaussianRandomFieldStore()

const panels = computed<number[]>({
  get: () => panelStore.panels.settings.individualGaussianRandomFields,
  set: (value: number[]) => {
    panelStore.set('settings', 'individualGaussianRandomFields', value)
    fieldStore.updateSimulations(fieldStore.selected)
  },
})

const deleteDialogRefs = ref<InstanceType<typeof ConfirmationDialog>[]>([])

const fields = computed<Field[]>(() => fieldStore.selected)

function addField(): void {
  fieldStore.addEmptyField()
}

async function deleteField(field: Field) {
  const fieldIndex = fields.value.findIndex((f) => f.id === field.id)

  const dialog = deleteDialogRefs.value[fieldIndex]
  const confirmed = await dialog?.open(
    'Are you sure?',
    `This will delete the Gaussian random field '${field.name}'`,
  )
  if (confirmed) fieldStore.remove(field)
}
</script>

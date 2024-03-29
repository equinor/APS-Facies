<template>
  <div>
    <confirmation-dialog v-if="warn" ref="confirmationDialog" />
    <v-select
      ref="selection"
      v-model.lazy="selected"
      :items="items"
      :disabled="disabled"
      :label="label"
      :loading="loading"
      variant="underlined"
    >
      <template #item="{ item, props }">
        <hover-helper v-slot="{ isHovering }">
          <v-list-item
            v-bind="props"
            :value="item.props.value"
            :disabled="item.props.disabled"
          >
            <base-tooltip
              :message="item.props.help"
              :open="isHovering && !!item.props.help"
              :disabled="!item.props.disabled && !item.props.help"
              trigger="manual"
              class="pa-0 ma-0"
            />
          </v-list-item>
        </hover-helper>
      </template>
    </v-select>
  </div>
</template>

<script setup lang="ts" generic="T">
import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog.vue'
import HoverHelper from '@/components/selection/dropdown/HoverHelper.vue'
import BaseTooltip from '@/components/baseComponents/BaseTooltip.vue'
import { VSelect } from 'vuetify/components'
import type { ListItem } from '@/utils/typing'
import { computed, ref } from 'vue'

type Props = {
  modelValue: T
  label: string
  items: ListItem<T>[]
  disabled?: boolean
  loading?: boolean
  warn?: boolean
  warnMessage?: string
  warnEvenWhenEmpty?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  loading: false,
  warn: false,
  warnMessage: '',
  warnEvenWhenEmpty: false,
})
const emit = defineEmits<{
  (event: 'update:model-value', value: T): void
}>()

const confirmationDialog = ref<InstanceType<typeof ConfirmationDialog> | null>(
  null,
)

const selected = computed({
  get: () => props.modelValue,
  set: (value: T) => {
    if (props.warn && (!!selected.value || props.warnEvenWhenEmpty)) {
      confirmationDialog.value
        ?.open('Are you sure?', props.warnMessage)
        .then((confirmed: boolean) => {
          if (confirmed) emit('update:model-value', value)
          else emit('update:model-value', selected.value)
        })
    } else {
      emit('update:model-value', value)
    }
  },
})
</script>

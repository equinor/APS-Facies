<template>
  <div>
    <confirmation-dialog v-if="warn" ref="confirmationDialog" />
    <v-select
      ref="selection"
      v-model.lazy="selected"
      :items="items"
      :disabled="disabled"
      :label="label"
    >
      <template #item="{ item, props }">
        <v-list-item
          :key="(props.key as string)"
          :value="item.raw.value"
          :disabled="item.raw.disabled"
          @click="props.onClick"
        >
          <v-hover v-slot="{ isHovering }">
            <base-tooltip
              :message="item.raw.help"
              :open="isHovering && !!item.raw.help"
              :disabled="!item.raw.disabled && !item.raw.help"
              trigger="manual"
              class="pa-0 ma-0"
            >
              <span :style="itemStyle(item.raw)">
                {{ item.raw.title }}
              </span>
            </base-tooltip>
          </v-hover>
        </v-list-item>
      </template>
    </v-select>
  </div>
</template>

<script setup lang="ts" generic="T">
import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog.vue'
import BaseTooltip from '@/components/baseComponents/BaseTooltip.vue'
import { VSelect } from 'vuetify/components'
import type { ListItem } from '@/utils/typing'
import { computed, ref } from 'vue'
import type { CSSProperties } from 'vue'

type Props = {
  modelValue: T
  label: string
  items: ListItem<T>[]
  disabled?: boolean
  warn?: boolean
  warnMessage?: string
  warnEvenWhenEmpty?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  disabled: false,
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

function itemStyle(item: ListItem<T>): CSSProperties {
  return item.disabled ? { color: 'rgba(0, 0, 0, 0.38)' } : {}
}
</script>

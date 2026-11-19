<template>
  <hover-helper v-slot="{ isHovering }">
    <floating-tooltip
      :shown="isHovering"
      :disabled="!tooltipText"
      placement="bottom"
      trigger="hover"
    >
      <v-btn
        :disabled="waiting || disabled"
        :theme="dark ? 'dark' : 'light'"
        :text="text"
        :color="color"
        :outlined="outlined"
        :variant="variant"
        @click="(e: MouseEvent) => emit('click', e)"
      >
        <slot v-if="!title && !waiting" />
        <span v-if="!waiting">
          {{ title }}
        </span>
        <span v-else>
          <v-progress-circular indeterminate />
        </span>
      </v-btn>
      <template #popper>
        {{ tooltipText }}
      </template>
    </floating-tooltip>
  </hover-helper>
</template>

<script setup lang="ts">
import HoverHelper from '@/components/selection/dropdown/HoverHelper.vue'
import type { Color } from '@/utils/domain/facies/helpers/colors'
import type { VBtn } from 'vuetify/components'

type Props = {
  title?: string
  tooltipText?: string
  waiting?: boolean
  disabled?: boolean
  outlined?: boolean
  text?: string
  dark?: boolean
  color?: Color
  variant?: VBtn['variant']
}

withDefaults(defineProps<Props>(), {
  title: '',
  tooltipText: '',
  waiting: false,
  disabled: false,
  outline: false,
  text: '',
  dark: false,
  color: undefined,
  variant: 'text',
})

const emit = defineEmits<{
  (event: 'click', value: MouseEvent): void
}>()
</script>

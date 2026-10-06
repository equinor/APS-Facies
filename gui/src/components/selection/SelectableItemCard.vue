<template>
  <v-card
    variant="outlined"
    class="item-card pt-1 px-2 pb-1"
    :class="{ 'item-card--current': isCurrent }"
    tabindex="0"
    :aria-current="isCurrent || undefined"
    @click="setCurrent"
    @keydown="onKeydown"
  >
    <div class="d-flex align-center ga-2">
      <v-checkbox-btn
        :model-value="selected === true"
        :indeterminate="selected === 'intermediate'"
        :aria-label="`Use ${name}`"
        density="compact"
        class="flex-grow-0"
        @click.stop="emit('toggle')"
      />
      <span class="text-body-2 text-truncate item-card__name">{{ name }}</span>
      <v-spacer />
      <span class="text-body-2 text-medium-emphasis text-no-wrap">
        Code {{ item.code }}
      </span>
      <v-menu location="bottom end">
        <template #activator="{ props: menuProps }">
          <v-btn
            v-bind="menuProps"
            icon="$more"
            variant="text"
            size="x-small"
            :aria-label="`Actions for ${name}`"
            @click.stop
          />
        </template>
        <v-list density="compact" min-width="160">
          <v-list-item prepend-icon="$copy" title="Copy" @click="copy" />
          <v-list-item
            prepend-icon="$paste"
            title="Paste"
            :disabled="!canPaste || isPasting"
            @click="paste"
          />
        </v-list>
      </v-menu>
    </div>
    <div v-if="$slots.settings" class="mt-1">
      <slot name="settings" />
    </div>
  </v-card>
</template>

<script setup lang="ts">
import type { Region, Zone } from '@/utils/domain'
import type { ID } from '@/utils/domain/types'
import type { SelectedType } from '@/utils/domain/bases/selectableItem'
import { computed } from 'vue'
import { useCopyPasteStore } from '@/stores/copy-paste'

const props = defineProps<{
  item: Zone | Region
  name: string
  selected: SelectedType
  isCurrent: boolean
}>()

const emit = defineEmits<{
  (event: 'update:current', value: ID): void
  (event: 'toggle'): void
}>()

defineSlots<{ settings?(): void }>()

const copyPasteStore = useCopyPasteStore()

const canPaste = computed(
  () => !!copyPasteStore.source && copyPasteStore.source.id !== props.item.id,
)
const isPasting = computed(() => !!copyPasteStore.isPasting(props.item))

function copy(): void {
  copyPasteStore.copy(props.item)
}

function paste(): void {
  copyPasteStore.paste(props.item)
}

function setCurrent(): void {
  emit('update:current', props.item.id)
}

// A key press on one of the controls the card contains, such as the checkbox
// or the actions menu, is left to that control
function onKeydown(event: KeyboardEvent): void {
  if (event.target !== event.currentTarget) return
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    setCurrent()
  }
}
</script>

<style lang="scss" scoped>
.item-card {
  border-color: rgba(var(--v-border-color), 0.22);
  border-radius: 14px;
}

.item-card__name {
  min-width: 0;
}

.item-card--current {
  border-color: rgb(var(--v-theme-accent));
  background-color: rgba(var(--v-theme-accent), 0.08);
}

.item-card:focus-visible {
  outline: 2px solid rgb(var(--v-theme-accent));
  outline-offset: 2px;
}
</style>

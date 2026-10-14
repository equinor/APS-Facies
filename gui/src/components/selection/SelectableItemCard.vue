<template>
  <v-card
    variant="outlined"
    class="item-card pt-1 px-2 pb-1"
    :class="{ 'item-card--current': isCurrent }"
    tabindex="0"
    :aria-current="isCurrent || undefined"
    @click="emit('activate')"
    @keydown="onKeydown"
  >
    <div class="d-flex align-center ga-2">
      <v-checkbox-btn
        :model-value="selected === true"
        :indeterminate="selected === 'intermediate'"
        :aria-label="`Use ${name}`"
        density="compact"
        class="flex-grow-0"
        :disabled="selectDisabled"
        @click.stop="emit('toggle')"
      />
      <slot name="prepend" />
      <span class="text-body-2 text-truncate item-card__name">{{ name }}</span>
      <v-spacer />
      <span
        class="item-card__code text-body-2 text-medium-emphasis text-no-wrap text-center"
      >
        Code {{ code }}
      </span>
      <v-menu v-if="$slots.actions" location="bottom end">
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
          <slot name="actions" />
        </v-list>
      </v-menu>
    </div>
    <div v-if="$slots.default" class="d-flex flex-column ga-1 mt-1">
      <slot />
    </div>
  </v-card>
</template>

<script setup lang="ts">
import type { SelectedType } from '@/utils/domain/bases/selectableItem'

withDefaults(
  defineProps<{
    name: string
    code: number
    selected: SelectedType
    isCurrent: boolean
    selectDisabled?: boolean
  }>(),
  { selectDisabled: false },
)

const emit = defineEmits<{
  (event: 'activate'): void
  (event: 'toggle'): void
}>()

defineSlots<{
  prepend?(): void
  actions?(): void
  default?(): void
}>()

// A key press on one of the controls the card contains, such as the checkbox
// or the actions menu, is left to that control
function onKeydown(event: KeyboardEvent): void {
  if (event.target !== event.currentTarget) return
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    emit('activate')
  }
}
</script>

<style lang="scss" scoped>
.item-card {
  --item-card-code-width: 4rem;
  border-color: rgba(var(--v-border-color), 0.22);
  border-radius: 14px;
}

.item-card__name {
  min-width: 0;
}

.item-card__code {
  min-width: var(--item-card-code-width);
}

.item-card--current {
  border-color: rgb(var(--v-theme-accent));
  background-color: rgba(var(--v-theme-accent), 0.08);
}

// Chromium 69 (RMS 14.2) shows a focus ring on click too, keep it for keyboard only
.item-card:focus {
  outline: none;
}

.item-card:focus-visible {
  outline: 2px solid rgb(var(--v-theme-accent));
  outline-offset: 2px;
}
</style>

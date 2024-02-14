<template>
  <v-row align="center" justify="center" no-gutters>
    <v-col cols="6">
      <v-col class="pa-0">
        <v-icon :disabled="!canDecrease" small @click="() => emit('input', -1)"
          >$up</v-icon
        >
      </v-col>
      <v-col class="pa-0">
        <v-icon :disabled="!canIncrease" small @click="() => emit('input', +1)"
          >$down</v-icon
        >
      </v-col>
    </v-col>
    <v-col cols="6">
      <v-col class="pa-0">
        <v-icon :disabled="!canRemove" small @click="() => emit('delete')"
          >$remove</v-icon
        >
        </v-col>
        <v-col class="pa-0">
        <v-icon :disabled="!canAdd" small @click="() => emit('add')">$add</v-icon>
      </v-col>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
type Props = {
  canIncrease?: boolean
  canDecrease?: boolean
  canRemove?: boolean
  canAdd?: boolean
}
withDefaults(defineProps<Props>(), {
  canIncrease: false,
  canDecrease: false,
  canRemove: false,
  canAdd: false,
})

const emit = defineEmits<{
  (event: 'input', value: 1 | -1): void
  (event: 'add'): void
  (event: 'delete'): void
}>()
</script>

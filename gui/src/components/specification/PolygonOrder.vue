<template>
  <v-row align="center" justify="center">
    <v-col cols="auto">
      <v-row>
        <polygon-order-button
          :disabled="!canDecrease"
          help="Move polygon up"
          icon="$up"
          @click="() => emit('input', -1)"
        />
      </v-row>
      <v-row>
        <polygon-order-button
          :disabled="!canIncrease"
          help="Move polygon down"
          icon="$down"
          @click="() => emit('input', +1)"
        />
      </v-row>
    </v-col>
    <v-col cols="auto">
      <v-row>
        <polygon-order-button
          :disabled="!canRemove"
          help="Remove this polygon"
          icon="$remove"
          @click="() => emit('delete')"
        />
      </v-row>
      <v-row>
        <polygon-order-button
          :disabled="!canAdd"
          help="Add a new polygon below this polygon"
          icon="$add"
          @click="() => emit('add')"
        />
      </v-row>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import PolygonOrderButton from './PolygonOrderButton.vue'
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

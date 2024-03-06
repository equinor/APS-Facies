<template>
  <v-card variant="elevated">
    <v-list-item>
      <v-list-item-title class="text-h5">
        {{ title }}
      </v-list-item-title>
    </v-list-item>
    <slot />
  </v-card>
</template>

<script setup lang="ts">
defineProps<{ title: string }>()
</script>

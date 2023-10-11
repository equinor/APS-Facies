<template>
  <v-row no-gutters>
    <h3>Alpha selection</h3>
    <alpha-fields :value="value" :min-fields="minFields" />
    <h3>Truncation rule specification background facies</h3>
    <v-row no-gutters>
      <v-col>
        <v-row no-gutters>
          <v-col>
            <component :is="table" :value="value" />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-row>
</template>

<script setup lang="ts">
import AlphaFields from '@/components/specification/TruncationRule/AlphaFields.vue'

import { TruncationRule } from '@/utils/domain'
import { computed } from 'vue'
import { type Component } from 'vue'

type Props = {
  value: TruncationRule
  table: Component
}
const props = defineProps<Props>()

const minFields = computed(() => (props.value.type === 'bayfill' ? 3 : 2))
</script>

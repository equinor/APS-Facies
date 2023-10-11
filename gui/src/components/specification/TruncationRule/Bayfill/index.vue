<template>
  <truncation-rule-specification :value="value" :table="PolygonTable" />
</template>

<script setup lang="ts">
import TruncationRuleSpecification from '@/components/specification/TruncationRule/main.vue'
import PolygonTable from './PolygonTable.vue'
import type { Bayfill } from '@/utils/domain'

defineProps<{ value: Bayfill }>()
</script>

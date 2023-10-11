<template>
  <truncation-rule-specification :value="value" :table="PolygonTable" />
</template>

<script setup lang="ts">
import TruncationRuleSpecification from '../main.vue'
import PolygonTable from './PolygonTable.vue'
import { Bayfill } from '@/utils/domain'

defineProps<{ value: Bayfill }>()
</script>

<template>
  <truncation-rule-specification :value="value" :table="PolygonTable" />
</template>

<script setup lang="ts">
import TruncationRuleSpecification from '../main.vue'
import PolygonTable from './table/index.vue'
import { Cubic } from '@/utils/domain'

defineProps<{ value: Cubic }>()
</script>

<template>
  <v-select
    v-model="selectedJob"
    label="RMS job"
    clearable
    :items="jobs"
    :disabled="loading"
    :loading="loading"
    variant="underlined"
  >
    <v-progress-linear indeterminate />
  </v-select>
</template>

<script setup lang="ts">
import { resetState, useStore } from '@/store'
import { getJobs } from '@/components/debugging/utils'
import { onMounted, computed, ref } from 'vue'

const store = useStore()

// TODO: "JSON" is probably not the correct type, probably meant "object".
const jobMapping = ref<Record<string, JSON>>({})
const selectedJob = ref<string | null>(null)

const loading = ref(false)

const jobs = computed(() => {
  return Object.keys(jobMapping.value)
})

onMounted(() => {
  loading.value = true
  getJobs()
    .then((receivedJobs) => {
      jobMapping.value = receivedJobs.reduce((jobDict, job) => {
        jobDict[job.instance_name] = JSON.parse(job.jobinputjson)
        return jobDict
      }, {} as Record<string, JSON>)
    })
    .finally(() => {
      loading.value = false
    })
})
</script>

<template>
  <v-select
    label="RMS job"
    :value="selectedJob"
    :items="jobs"
    :append-outer-icon="clearIcon"
    :disabled="loading"
    :loading="loading"
    @change="(job: string) => selectJob(job)"
    @click:append-outer="clear"
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

const clearIcon = computed(() => {
  return selectedJob.value ? '$vuetify.icons.values.clear' : ''
})

function selectJob(job: string): void {
  selectedJob.value = job
  const state = jobMapping.value[job]
  store.dispatch('populate', state)
}

function clear(): void {
  selectedJob.value = null
  resetState()
}

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

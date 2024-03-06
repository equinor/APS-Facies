<template>
  <v-autocomplete
    v-model="selectedJob"
    label="RMS job"
    clearable
    :items="jobs"
    :disabled="loading"
    :loading="loading"
    variant="underlined"
  >
    <v-progress-linear indeterminate />
  </v-autocomplete>
</template>

<script setup lang="ts">
import { getJobs } from '@/components/debugging/utils'
import { onMounted, computed, ref } from 'vue'
import type { RootStoreSerialization } from '@/stores'
import { useRootStore } from '@/stores'

const rootStore = useRootStore()

type Jobs = Record<string, RootStoreSerialization>

const jobMapping = ref<Jobs>({})
const loading = ref(false)

const _selectedJob = ref<string | null>(null)
const selectedJob = computed({
  get: () => _selectedJob.value,
  set: (job: keyof Jobs | null) => {
    _selectedJob.value = job
    if (!job) {
      rootStore.$reset()
    } else {
      rootStore.populate(jobMapping.value[job])
    }
  },
})

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
      }, {} as Jobs)
    })
    .finally(() => {
      loading.value = false
    })
})
</script>

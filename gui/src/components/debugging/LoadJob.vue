<template>
  <v-select
    label="RMS job"
    :value="selectedJob"
    :items="jobs"
    :append-outer-icon="clearIcon"
    :disabled="loading"
    :loading="loading"
    @change="job => selectJob(job)"
    @click:append-outer="clear"
  >
    <v-progress-linear
      v-slot:progress
      indeterminate
    />
  </v-select>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { resetState } from '@/store'
import { getJobs } from '@/components/debugging/utils'

@Component
export default class LoadJob extends Vue {
  private jobMapping: Record<string, JSON> = {}
  private selectedJob: string | null = null

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  private loading = false // TypeScript complains it is not read, even though it is used in the template

  get jobs (): string[] {
    return Object.keys(this.jobMapping)
  }

  get clearIcon (): string { return this.selectedJob ? '$vuetify.icons.values.clear' : '' }

  selectJob (job: string): void {
    this.selectedJob = job
    const state = this.jobMapping[job]
    this.$store.dispatch('populate', state)
  }

  clear (): void {
    this.selectedJob = null
    resetState()
  }

  mounted (): void {
    this.loading = true
    getJobs()
      .then(jobs => {
        this.jobMapping = jobs
          .reduce((jobs, job) => {
            jobs[job.instance_name] = JSON.parse(job.jobinputjson)
            return jobs
          }, ({} as Record<string, JSON>))
      })
      .finally(() => {
        this.loading = false
      })
  }
}
</script>

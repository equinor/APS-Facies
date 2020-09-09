<template>
  <v-select
    label="RMS job"
    :value="selectedJob"
    :items="jobs"
    :append-outer-icon="clearIcon"
    @change="job => selectJob(job)"
    @click:append-outer="clear"
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { resetState } from '@/store'
import { getJobs } from '@/components/debugging/utils'

@Component
export default class LoadJob extends Vue {
  private jobMapping: Record<string, JSON> = {}
  private selectedJob: string | null = null

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
    getJobs()
      .then(jobs => {
        this.jobMapping = jobs
          .reduce((jobs, job) => {
            jobs[job.instance_name] = JSON.parse(job.jobinputjson)
            return jobs
          }, ({} as Record<string, JSON>))
      })
  }
}
</script>

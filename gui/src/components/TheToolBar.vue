<template>
  <v-toolbar color="#ffffff">
    <v-spacer />
    <v-row v-if="isDevelop">
      <load-job />
      <run-job />
      <export-state />
    </v-row>
    <v-btn v-if="false" disabled variant="outlined" color="primary">
      Run Settings
    </v-btn>
    <div class="d-flex ga-3">
      <job-settings />
      <action-button
        v-tooltip:bottom="
          'Documentation of the APS methodology and user guide for this plug-in.'
        "
        append-icon="$externalLink"
        @click="goToHelp"
      >
        Documentation
      </action-button>
      <action-button @click="openChangelog"> Release notes </action-button>
      <action-button
        :loading="refreshing"
        :disabled="refreshing"
        @click="refresh"
      >
        Refresh gathered RMS data
      </action-button>
    </div>
    <changelog-dialog ref="changelogDialog" />
  </v-toolbar>
</template>

<script setup lang="ts">
import ChangelogDialog from '@/components/dialogs/ChangelogDialog.vue'
import JobSettings from '@/components/dialogs/JobSettings/index.vue'
import ActionButton from '@/components/baseComponents/ActionButton.vue'
import ExportState from '@/components/debugging/exportState.vue'
import LoadJob from '@/components/debugging/LoadJob.vue'
import RunJob from '@/components/debugging/RunJob.vue'
import rms from '@/api/rms'
import { isDevelopmentBuild } from '@/utils/helpers/simple'
import { ref } from 'vue'
import { useRootStore } from '@/stores'

const isDevelop = isDevelopmentBuild()
const rootStore = useRootStore()

const refreshing = ref(false)
const changelogDialog = ref<InstanceType<typeof ChangelogDialog> | null>(null)

function goToHelp(): void {
  rms.openWikiHelp()
}

function openChangelog(): void {
  changelogDialog.value?.open()
}

async function refresh(): Promise<void> {
  refreshing.value = true
  await rootStore.refresh('Fetching data from RMS')
  refreshing.value = false
}
</script>

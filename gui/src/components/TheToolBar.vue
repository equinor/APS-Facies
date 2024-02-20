<template>
  <v-toolbar color="#ffffff">
    <!--
      NOTE: the attribute 'flat' has been replaced with 'color=""', as to avoid  mutating a prop directly
      This is *exactly* the same as what's done in the source code for the upload button
    -->
    <icon-button
      ref="uploadButton"
      v-tooltip.bottom="'Import an existing model file'"
      color="black"
      icon="import"
      @click="importModelFile"
    />
    <icon-button
      v-tooltip.bottom="'Export the current specification as a model file'"
      icon="export"
      @click="exportModelFile"
    />
    <export-dialog ref="exportDialog" />
    <v-spacer />
    <v-row v-if="isDevelop">
      <load-job />
      <run-job />
      <export-state />
    </v-row>
    <job-settings />
    <v-btn v-if="false" disabled variant="outlined" color="primary"> Run Settings </v-btn>
    <icon-button
      icon="changelog"
      color="primary"
      v-tooltip.bottom="`What's new?`"
      @click="() => openChangelog()"
    />
    <changelog-dialog ref="changelogDialog" />
    <icon-button
      icon="help"
      color="primary"
      @click="() => goToHelp()"
      v-tooltip="
        'Documentation of the APS methodology and user guide for this plug-in.'
      "
    />
    <span v-if="betaBuild">
      {{ `${versionInformation}` }}
    </span>
    <icon-button
      v-tooltip.bottom="'Refreshes the data gathered from RMS'"
      icon="refresh"
      :waiting="refreshing"
      @click="refresh"
    />
  </v-toolbar>
</template>

<script setup lang="ts">
import { displayError, displaySuccess } from '@/utils/helpers/storeInteraction'
import ExportDialog from '@/components/dialogs/ExportDialog.vue'
import ChangelogDialog from '@/components/dialogs/ChangelogDialog.vue'
import JobSettings from '@/components/dialogs/JobSettings/index.vue'
import IconButton from '@/components/selection/IconButton.vue'
import ExportState from '@/components/debugging/exportState.vue'
import LoadJob from '@/components/debugging/LoadJob.vue'
import RunJob from '@/components/debugging/RunJob.vue'
import type { Optional } from '@/utils/typing'
import rms from '@/api/rms'
import { isDevelopmentBuild } from '@/utils/helpers/simple'
import { ref } from 'vue'
import { XMLParser } from 'fast-xml-parser'
import { useModelFileExporterStore } from '@/stores/model-file-exporter'
import { useRootStore } from '@/stores'
import { useModelFileLoaderStore } from '@/stores/model-file-loader'
import { APSError } from '@/utils/domain/errors'
import type { ID } from '@/utils/domain/types'
import { v4 as uuidv4 } from 'uuid'

const betaBuild: boolean = import.meta.env.VUE_APP_BUILD_MODE !== 'stable'
const versionNumber: Optional<string> =
  import.meta.env.VUE_APP_APS_VERSION || null
const buildNumber: Optional<string> =
  import.meta.env.VUE_APP_BUILD_NUMBER || null
const commitHash: Optional<string> = import.meta.env.VUE_APP_HASH || null
const versionInformation: string =
  versionNumber && buildNumber && commitHash
    ? `${versionNumber}.${buildNumber}-${commitHash} (beta)`
    : 'live'
const isDevelop = isDevelopmentBuild()
const rootStore = useRootStore()

async function loadModelFile(
  fileName: string,
  fileContent: string | null = null,
): Promise<void> {
  let json: string | null = null

  rootStore.startLoading(`Checking the model file, "${fileName}", for consistency`)
  if (!fileContent) fileContent = await rms.loadFile(fileName)

  if (!fileContent) {
    displayError('The file is empty, or it does not exist')
  } else {
    try {
      let polygonOrder = 0
      let previousPath: string | null = null

      class Node {
        public id: ID
        public parent: Node | null
        public children: Node[]
        constructor(root: null | Node) {
          this.id = uuidv4()
          this.parent = root
          this.children = []
          if (root) {
            root.add(this)
          }

        }
        public add(child: Node): void {
          child.parent = this
          this.children.push(child)
        }
      }

      let node: Node | null = null
      const xmlParser = new XMLParser({
        ignoreAttributes: false,
        trimValues: true,
        updateTag(tagName, jPath, attrs) {
          if (jPath.includes('Trunc2D_Cubic.BackGroundModel')) {
            if (/\.L\d+(\.ProbFrac)?$/.test(jPath)) {
              const previousLevel: number = previousPath?.replace('.ProbFrac', '').split('.').length ?? 0
              const currentLevel = jPath.replace('.ProbFrac', '').split('.').length
              if (previousLevel === 0 || previousPath === null) {
                // New cubic truncation rule
                node = new Node(null)
              } else if (currentLevel > previousLevel) {
                // We go down one level
                node = new Node(node)
              } else if (currentLevel < previousLevel) {
                // We go up one level
                node = node!.parent
                if (/^L\d+$/.test(tagName)) {
                  // That is, is a new level, adjacent to the previous
                  node = new Node(node!.parent)
                }
              } else if (previousPath?.endsWith('ProbFrac') && /L\d+$/.test(tagName)) {
                // That is, we go up one level from a leaf / ProgFrac to a new 'empy' node
                node = new Node(node!.parent)
              } else if (/L\d+$/.test(previousPath ?? '') && tagName === 'ProbFrac') {
                // That is, we go from a 'node' down to a new level
              }

              if (/L\d+/.test(tagName)) {
                if (!node) throw new APSError('Uninitialized tree')

                attrs['@_id'] = node.id
                attrs['@_parentId'] = node.parent?.id ?? ''
                attrs['@_order'] = polygonOrder.toString(10)
                polygonOrder += 1
              }

              if (tagName === 'ProbFrac') {
                if (node === null) throw new APSError('<L1> is Missing from <Trunc2D_Cubic><BackGroundModel>')
                attrs['@_order'] = polygonOrder.toString(10)
                attrs['@_parentId'] = node.id

                polygonOrder += 1
              }

              previousPath = jPath
            }
          }
          if (tagName === 'TruncationRule') {
            // Reset order for each truncation rule
            polygonOrder = 0
            previousPath = null
            node = null
          }
          return tagName
        },
      })
      const jsObject = xmlParser.parse(fileContent)
      json = JSON.stringify(jsObject)
    } catch (err: any) {
      displayError(
        'The file you tried to open is not valid XML and cannot be used\n' +
          'Fix the following error before opening again:\n\n' +
          err.message,
      )
    }
    if (json) {
      const { valid, error } = await rms.isApsModelValid(btoa(fileContent))
      if (valid) {
        rootStore.$reset()
        rootStore.loadingMessage = 'Resetting the state...'
        await rootStore.fetch()
        await useModelFileLoaderStore()
          .populateGUI(json, fileName)

      } else {
        displayError(
          'The file you tried to open is not a valid APS model file and cannot be used\n' +
            'Fix the following error before opening again:\n\n' +
            error,
        )
      }
    }
  }

  rootStore.finishLoading()
}

const refreshing = ref(false)
const lastMSelectedModelFile = ref('')
const changelogDialog = ref<InstanceType<typeof ChangelogDialog> | null>(null)
const exportDialog = ref<InstanceType<typeof ExportDialog> | null>(null)

function goToHelp(): void {
  rms.openWikiHelp()
}

function openChangelog(): void {
  changelogDialog.value?.open()
}

async function importModelFile(): Promise<void> {
  if (isDevelop) {
    const input = document.createElement('input')
    input.type = 'file'
    input.onchange = (event: Event): void => {
      const { files } = event.target as HTMLInputElement
      if (files) {
        const file = files[0]
        file.text().then((content) => loadModelFile(file.name, content))
      }
      input.remove()
    }
    input.click()
  } else {
    const fileName = await rms.chooseFile(
      'load',
      'APS model files (*.xml)',
      lastMSelectedModelFile.value,
    )
    if (fileName) {
      lastMSelectedModelFile.value = fileName
      await loadModelFile(fileName)
    }
  }
}

async function refresh(): Promise<void> {
  refreshing.value = true
  await rootStore.refresh('Fetching data from RMS')
  refreshing.value = false
}

async function exportModelFile(): Promise<void> {
  const modelFileExporterStore = useModelFileExporterStore()
  const exportedXMLString = await modelFileExporterStore
    .createModelFileFromStore()
    .catch(async (error) => {
      displayError(error.message)
    })
  if (exportedXMLString) {
    const result = await rms.isApsModelValid(btoa(exportedXMLString))
    if (result.valid) {
      const response = await exportDialog.value?.open()
      if (response?.paths) {
        const resultPromise = rms.saveModel(
          btoa(exportedXMLString),
          response.paths,
        )
        resultPromise.then(async (success: boolean): Promise<void> => {
          if (success) {
            displaySuccess(
              `The model file was saved to ${response.paths?.model ?? '-'}`,
            )
          }
        })
          .catch(err => {
            displayError(err)
          })
      }
    } else {
      displayError(
        'The model you have defined is not valid and cannot be exported\n' +
          'Fix the following error before exporting again:\n\n' +
          result.error,
      )
    }
  }
}
</script>

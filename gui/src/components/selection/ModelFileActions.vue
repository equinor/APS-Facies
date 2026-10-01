<template>
  <div class="d-flex flex-column ga-2">
    <action-button
      v-tooltip:bottom="'Import an existing model file'"
      block
      @click="importModelFile"
    >
      Import Model File
    </action-button>
    <action-button
      v-tooltip:bottom="'Export the current specification as a model file'"
      block
      @click="exportModelFile"
    >
      Export Model File
    </action-button>
    <export-dialog ref="exportDialog" />
  </div>
</template>

<script setup lang="ts">
import { displayError, displaySuccess } from '@/utils/helpers/storeInteraction'
import ExportDialog from '@/components/dialogs/ExportDialog.vue'
import ActionButton from '@/components/baseComponents/ActionButton.vue'
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

const isDevelop = isDevelopmentBuild()
const rootStore = useRootStore()

const lastMSelectedModelFile = ref('')
const exportDialog = ref<InstanceType<typeof ExportDialog> | null>(null)

async function loadModelFile(
  fileName: string,
  fileContent: string | null = null,
): Promise<void> {
  let json: string | null = null

  rootStore.startLoading(
    `Checking the model file, "${fileName}", for consistency`,
  )
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
          if (typeof jPath !== 'string') {
            jPath = jPath.toString()
          }
          if (jPath.includes('Trunc2D_Cubic.BackGroundModel')) {
            if (/\.L\d+(\.ProbFrac)?$/.test(jPath)) {
              const previousLevel: number =
                previousPath?.replace('.ProbFrac', '').split('.').length ?? 0
              const currentLevel = jPath
                .replace('.ProbFrac', '')
                .split('.').length
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
              } else if (
                previousPath?.endsWith('ProbFrac') &&
                /L\d+$/.test(tagName)
              ) {
                // That is, we go up one level from a leaf / ProgFrac to a new 'empy' node
                node = new Node(node!.parent)
              } else if (
                /L\d+$/.test(previousPath ?? '') &&
                tagName === 'ProbFrac'
              ) {
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
                if (node === null)
                  throw new APSError(
                    '<L1> is Missing from <Trunc2D_Cubic><BackGroundModel>',
                  )
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
    } catch (err) {
      displayError(
        'The file you tried to open is not valid XML and cannot be used\n' +
          'Fix the following error before opening again:\n\n' +
          (err as Error).message,
      )
    }
    if (json) {
      const { valid, error } = await rms.isApsModelValid(btoa(fileContent))
      if (valid) {
        rootStore.$reset()
        await rootStore.fetch('Resetting the state...')
        await useModelFileLoaderStore().populateGUI(json, fileName)
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

async function importModelFile(): Promise<void> {
  if (isDevelop) {
    const input = document.createElement('input')
    input.type = 'file'
    input.onchange = (event: Event): void => {
      const { files } = event.target as HTMLInputElement
      if (files && files.length >= 1 && files[0]) {
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

async function exportModelFile(): Promise<void> {
  const modelFileExporterStore = useModelFileExporterStore()
  const exportedXMLString = await modelFileExporterStore
    .createModelFileFromStore(true)
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
        resultPromise
          .then(async (success: boolean): Promise<void> => {
            if (success) {
              displaySuccess(
                `The model file was saved to ${response.paths?.model ?? '-'}`,
              )
            }
          })
          .catch((err) => {
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

<template>
  <v-dialog v-model="dialog" max-width="1000px" @keydown.esc="close">
    <v-card>
      <v-row>
        <v-spacer />
        <v-col>
          <div id="changelog" v-html="changelog" />
        </v-col>
        <v-spacer />
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import md from '@/plugins/markdown'
import { onMounted, ref } from 'vue'

// 'axios' does not work as expected in RMS 11
// when moving 'axios' from devDependencies
const axios: { get: (url: string) => Promise<{ data: string }> } = {
  get(url: string): Promise<{ data: string }> {
    return new Promise((resolve) => {
      const client = new XMLHttpRequest()
      client.open('GET', url)
      client.onreadystatechange = (): void => {
        if (client.readyState === XMLHttpRequest.DONE) {
          resolve({
            data: client.responseText,
          })
        }
      }
      client.send()
    })
  },
}

const dialog = ref(false)
const changelog = ref('')

function close() {
  dialog.value = false
}
function open() {
  dialog.value = true
}
defineExpose({ open })

async function fetchChangelog(): Promise<void> {
  const { data } = await axios.get('/CHANGELOG.md')
  changelog.value = md.render(data)
}

onMounted(fetchChangelog)
</script>

<style lang="scss">
#changelog {
  flex: auto;
}
</style>

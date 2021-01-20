<template>
  <v-dialog
    v-model="dialog"
    max-width="1000px"
    @keydown.esc="close"
  >
    <v-card>
      <v-row>
        <v-spacer />
        <v-col>
          <div
            id="changelog"
            v-html="changelog"
          />
        </v-col>
        <v-spacer />
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import md from '@/plugins/markdown'

// 'axios' does not work as expected in RMS 11
// when moving 'axios' from devDependencies
const axios: { get: (url: string) => Promise<{data: string}> } = {
  get (url: string): Promise<{ data: string }> {
    return new Promise(resolve => {
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
  }
}

@Component({})
export default class ChangelogDialog extends Vue {
  public dialog = false
  public changelog = ''

  async fetchChangelog (): Promise<void> {
    const { data } = await axios.get('/CHANGELOG.md')
    this.changelog = md.render(data)
  }

  mounted (): void {
    this.fetchChangelog()
  }

  public close (): void { this.dialog = false }

  public open (): void { this.dialog = true }
}
</script>

<style lang="scss">
  #changelog {
    flex: auto;
  }
</style>

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

import axios from 'axios'
import md from '@/plugins/markdown'

@Component({})
export default class ChangelogDialog extends Vue {
  public dialog = false
  public changelog = ''

  async fetchChangelog () {
    const { data } = await axios.get('/CHANGELOG.md')
    this.changelog = md.render(data)
  }

  mounted () {
    this.fetchChangelog()
  }

  public close () { this.dialog = false }

  public open () { this.dialog = true }
}
</script>

<style lang="scss">
  #changelog {
    flex: auto;
  }
</style>

<template>
  <v-expansion-panel>
    <v-expansion-panel-header v-slot="{ open }">
      <v-row
        class="pa-0 ma-0"
        justify="center"
        align="center"
      >
        <v-col>
          <section-title>Gaussian Random Fields (GRF)</section-title>
        </v-col>
        <v-col
          v-show="open"
          cols="2"
        >
          <icon-button
            icon="add"
            @click="addField"
          />
        </v-col>
      </v-row>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <cross-section />
      <v-expansion-panels
        v-model="panel"
        accordion
      >
        <v-expansion-panel
          v-for="field in fields"
          :key="field.id"
        >
          <v-expansion-panel-header>
            <v-row
              class="fill-height"
              align="center"
              justify="start"
            >
              <v-col cols="4">
                <gaussian-field-name
                  :ref="field.id"
                  :value="field"
                />
              </v-col>
              <v-col
                cols="1"
              >
                <icon-button
                  icon="remove"
                  @click.stop="deleteField(field)"
                />
                <confirmation-dialog :ref="`confirmation_${field.id}`" />
              </v-col>
            </v-row>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <gaussian-random-field
              :value="field"
            />
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import GaussianRandomField from '@/components/specification/GaussianRandomField/index.vue'
import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog.vue'
import GaussianFieldName from '@/components/specification/GaussianRandomField/GaussianFieldName.vue'
import IconButton from '@/components/selection/IconButton.vue'
import CrossSection from '@/components/specification/GaussianRandomField/CrossSection.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'

import { GaussianRandomField as Field } from '@/utils/domain'
import { ID } from '@/utils/domain/types'
import { isNumber } from 'lodash'

@Component({
  components: {
    SectionTitle,
    CrossSection,
    IconButton,
    GaussianFieldName,
    ConfirmationDialog,
    GaussianRandomField,
  },
})
export default class MultipleGaussianRandomFields extends Vue {
  get panel (): number { return this.$store.state.panels.settings.gaussianRandomFields }
  set panel (value) { this.$store.dispatch('panels/set', { type: 'settings', panel: 'gaussianRandomFields', toggled: isNumber(value) ? value : true }) }

  get fields (): Field[] { return this.$store.getters.fields }
  get ids (): ID[] { return Object.keys(this.fields) }

  async addField (): Promise<void> {
    await this.$store.dispatch('gaussianRandomFields/addEmptyField')
  }

  deleteField (field: Field): void {
    this.$refs[`confirmation_${field.id}`][0].open('Are you sure?', `This will delete the Gaussian random field '${field.name}'`)
      .then((confirmed: boolean) => {
        if (confirmed) this.$store.dispatch('gaussianRandomFields/deleteField', { field })
      })
  }
}
</script>
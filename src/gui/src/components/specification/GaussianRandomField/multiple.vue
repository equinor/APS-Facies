<template>
  <v-expansion-panel>
    <v-expansion-panel-header v-slot="{ open }">
      <v-layout
        justify-center
        align-center
        pa-0
        ma-0
      >
        <v-flex>
          <section-title>Gaussian Random Fields (GRF)</section-title>
        </v-flex>
        <v-flex
          v-show="open"
          xs2
        >
          <icon-button
            icon="add"
            @click="addField"
          />
        </v-flex>
      </v-layout>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <cross-section />
      <v-expansion-panels
        accordion
      >
        <v-expansion-panel
          v-for="field in fields"
          :key="field.id"
        >
          <v-expansion-panel-header>
            <v-layout
              align-center
              justify-start
              fill-height
              wrap
            >
              <v-flex xs2>
                <gaussian-field-name
                  :ref="field.id"
                  :value="field"
                />
              </v-flex>
              <v-flex
                xs1
              >
                <icon-button
                  icon="remove"
                  @click.stop="deleteField(field)"
                />
                <confirmation-dialog :ref="`confirmation_${field.id}`" />
              </v-flex>
            </v-layout>
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
  get fields () { return this.$store.getters['fields'] }
  get ids () { return Object.keys(this.fields) }

  async addField () {
    await this.$store.dispatch('gaussianRandomFields/addEmptyField')
  }

  deleteField (field: Field) {
    this.$refs[`confirmation_${field.id}`][0].open('Are you sure?', `This will delete the Gaussian random field '${field.name}'`)
      .then((confirmed: boolean) => {
        if (confirmed) this.$store.dispatch('gaussianRandomFields/deleteField', { field })
      })
  }
}
</script>

<template>
  <v-expansion-panel
    v-model="expanded"
  >
    <v-expansion-panel-content>
      <div slot="header">
        <v-layout
          justify-center
          align-center
          row
          pa-0
          ma-0
        >
          <v-flex>
            <h2>Gaussian Random Fields (GRF)</h2>
          </v-flex>
          <v-flex
            v-show="isOpen"
            xs2
          >
            <icon-button
              icon="add"
              @click="addField"
            />
          </v-flex>
        </v-layout>
      </div>
      <v-expansion-panel>
        <v-expansion-panel-content
          v-for="field in fields"
          :key="field.id"
        >
          <div slot="header">
            <v-layout
              align-center
              justify-start
              row
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
          </div>
          <v-card>
            <gaussian-random-field
              :value="field"
            />
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import { mapGetters } from 'vuex'

import GaussianRandomField from '@/components/specification/GaussianRandomField'
import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog'
import GaussianFieldName from '@/components/specification/GaussianRandomField/GaussianFieldName'
import IconButton from '@/components/selection/IconButton'

export default {
  components: {
    IconButton,
    GaussianFieldName,
    ConfirmationDialog,
    GaussianRandomField,
  },

  data () {
    return {
      expanded: null,
    }
  },

  computed: {
    ...mapGetters({
      fields: 'fields'
    }),
    isOpen () { return this.expanded === 0 },
    ids () { return Object.keys(this.fields) },
  },

  methods: {
    addField () {
      this.$store.dispatch('gaussianRandomFields/addEmptyField')
    },
    deleteField (field) {
      this.$refs[`confirmation_${field.id}`][0].open('Are you sure?', `This will delete the Gaussian random field '${field.name}'`, {})
        .then(confirmed => {
          if (confirmed) this.$store.dispatch('gaussianRandomFields/deleteField', { grfId: field.id })
        })
    },
  }
}
</script>

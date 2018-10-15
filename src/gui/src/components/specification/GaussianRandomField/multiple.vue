<template>
  <div>
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
      <v-flex xs2>
        <v-btn
          icon
          @click="addField"
        >
          <v-icon>add_box</v-icon>
        </v-btn>
      </v-flex>
    </v-layout>
    <v-expansion-panel>
      <v-expansion-panel-content
        v-for="grfId in ids"
        :key="grfId"
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
                :ref="grfId"
                :grf-id="grfId"
              />
            </v-flex>
            <v-flex
              xs1
            >
              <v-btn
                flat
                icon
                @click.stop="deleteField(grfId)"
              >
                <v-icon>delete</v-icon>
              </v-btn>
              <confirmation-dialog :ref="`confirmation_${grfId}`"/>
            </v-flex>
          </v-layout>
        </div>
        <v-card>
          <gaussian-random-field
            :grf-id="grfId"
          />
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </div>
</template>

<script>
import GaussianRandomField from '@/components/specification/GaussianRandomField'
import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog'
import GaussianFieldName from '@/components/specification/GaussianRandomField/GaussianFieldName'

export default {
  components: {
    GaussianFieldName,
    ConfirmationDialog,
    GaussianRandomField,
  },

  computed: {
    fields () { return this.$store.state.gaussianRandomFields.fields },
    ids () { return Object.keys(this.fields) },
  },

  methods: {
    addField () {
      this.$store.dispatch('gaussianRandomFields/addEmptyField')
    },
    deleteField (grfId) {
      this.$refs[`confirmation_${grfId}`][0].open('Are you sure?', `This will delete the Gaussian random field '${this.fields[`${grfId}`].name}'`, {})
        .then(confirmed => {
          if (confirmed) this.$store.dispatch('gaussianRandomFields/deleteField', { grfId })
        })
    },
  }
}
</script>

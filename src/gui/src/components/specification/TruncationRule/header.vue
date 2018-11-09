<template>
  <v-layout row>
    <v-flex xs5>
      <v-select
        v-model="type"
        :items="truncationRules"
        label="Rule"
      />
    </v-flex>
    <v-flex xs5>
      <v-combobox
        v-model="template"
        :items="templates"
        :disabled="!type"
        label="Template"
      />
    </v-flex>
    <icon-button
      icon="add"
      disabled
      @click="addTemplate"
    />
    <icon-button
      icon="copy"
      disabled
      @click="copyTemplate"
    />
    <icon-button
      icon="remove"
      disabled
      @click="deleteTemplate"
    />
  </v-layout>
</template>

<script>
import { mapGetters, mapState } from 'vuex'
import IconButton from '@/components/selection/IconButton'

export default {
  name: 'TruncationHeader',

  components: {
    IconButton
  },

  computed: {
    ...mapGetters({
      truncationRules: 'truncationRules/ruleTypes',
      templates: 'truncationRules/ruleNames'
    }),
    ...mapState({
      preset: state => state.truncationRules.preset
    }),
    type: {
      get: function () {
        const type = this.$store.state.truncationRules.templates.types.available[this.preset.type]
        return type
          ? type.name
          : ''
      },
      set: function (type) { this.$store.dispatch('truncationRules/changePreset', { type }) }
    },
    template: {
      get: function () { return this.preset.template },
      set: function (template) { this.$store.dispatch('truncationRules/changePreset', { template }) },
    },
  },

  methods: {
    addTemplate () {},
    copyTemplate () {},
    deleteTemplate () {},
  },
}
</script>

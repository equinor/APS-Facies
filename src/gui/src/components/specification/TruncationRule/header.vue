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
import { mapGetters } from 'vuex'
import IconButton from '@/components/selection/IconButton'
import { isUUID } from '@/utils/helpers'

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
    preset () {
      const rule = this.$store.getters.truncationRule
      const { type, template } = this.$store.state.truncationRules.preset
      return {
        type: type || (rule ? rule.type : ''),
        template: template || {
          text: rule ? rule.name : '',
        },
      }
    },
    type: {
      get: function () {
        let type = this.preset.type
        if (!!type && isUUID(type)) {
          type = this.$store.state.truncationRules.templates.types.available[`${type}`]
        } else if (!!type && !isUUID(type)) {
          type = Object.values(this.$store.state.truncationRules.templates.types.available).find(item => item.type === type)
        }
        return type
          ? type.name
          : ''
      },
      set: function (type) { this.$store.dispatch('truncationRules/preset/change', { type }) }
    },
    template: {
      get: function () { return this.preset.template },
      set: function (template) { this.$store.dispatch('truncationRules/preset/change', { template }) },
    },
  },

  methods: {
    addTemplate () {},
    copyTemplate () {},
    deleteTemplate () {},
  },
}
</script>

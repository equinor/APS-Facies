<template>
  <v-layout>
    <v-flex>
      <v-select
        ref="chooseTruncationRuleType"
        v-model="type"
        :items="truncationRules"
        label="Rule"
      />
    </v-flex>
    <v-flex>
      <v-combobox
        ref="chooseTruncationRuleTemplate"
        v-model="template"
        :items="templates"
        :disabled="!type"
        label="Template"
      />
    </v-flex>
    <v-flex
      v-if="false"
      xs6
    >
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
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { RootGetters, RootState } from '@/store/typing'

import IconButton from '@/components/selection/IconButton.vue'
import { isUUID } from '@/utils/helpers'

@Component({
  components: {
    IconButton
  },
})
export default class TruncationHeader extends Vue {
  get truncationRules () { return (this.$store.getters as RootGetters)['truncationRules/ruleTypes'] }
  get templates () { return (this.$store.getters as RootGetters)['truncationRules/ruleNames'] }

  get preset () {
    const rule = this.$store.getters.truncationRule
    const { type, template } = this.$store.state.truncationRules.preset
    return {
      type: type || (rule ? rule.type : ''),
      template: template || {
        text: rule ? rule.name : '',
      },
    }
  }

  get type () {
    let type = this.preset.type
    if (!!type && isUUID(type)) {
      type = this.$store.state.truncationRules.templates.types.available[`${type}`]
    } else if (!!type && !isUUID(type)) {
      type = Object.values((this.$store.state as RootState).truncationRules.templates.types.available).find(item => item.type === type)
    }
    return type
      ? type.name
      : ''
  }
  set type (type) { this.$store.dispatch('truncationRules/preset/change', { type }) }

  get template () { return this.preset.template }
  set template (template) { this.$store.dispatch('truncationRules/preset/change', { template }) }

  addTemplate () {}
  copyTemplate () {}
  deleteTemplate () {}
}
</script>

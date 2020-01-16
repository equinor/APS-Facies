<template>
  <v-row no-gutters>
    <v-col>
      <v-select
        ref="chooseTruncationRuleType"
        v-model="type"
        :items="truncationRules"
        label="Rule"
      />
    </v-col>
    <v-col>
      <v-combobox
        ref="chooseTruncationRuleTemplate"
        v-model="template"
        :items="templates"
        :disabled="!type"
        label="Template"
      >
        <template v-slot:item="{ item }">
          <truncation-rule-preview
            :value="item.text"
            :type="type"
            :disabled="item.disabled"
          />
        </template>
      </v-combobox>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { RootGetters, RootState } from '@/store/typing'

import IconButton from '@/components/selection/IconButton.vue'
import TruncationRulePreview from './TruncationRulePreview.vue'

import { isUUID } from '@/utils/helpers'

@Component({
  components: {
    TruncationRulePreview,
    IconButton,
  },
})
export default class TruncationHeader extends Vue {
  get truncationRules (): { text: string, disabled: boolean, order: number }[] { return (this.$store.getters as RootGetters)['truncationRules/ruleTypes'] }
  get templates (): { text: string, disabled: boolean }[] { return (this.$store.getters as RootGetters)['truncationRules/ruleNames'] }

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

  get type (): string {
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
}
</script>

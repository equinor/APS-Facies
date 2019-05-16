<template>
  <v-container column>
    <h4>Alpha selection</h4>
    <v-layout row>
      <alpha-fields
        :value="value"
        :min-fields="minFields"
      />
    </v-layout>
    <h4>Truncation rule specification</h4>
    <v-layout>
      <v-flex>
        <v-layout>
          <v-flex>
            <component
              :is="table"
              :value="value"
            />
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import AlphaFields from '@/components/specification/TruncationRule/AlphaFields.vue'

import { TruncationRule } from '@/utils/domain'

@Component({
  components: {
    AlphaFields,
  },
})
export default class TruncationRuleSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: TruncationRule

  @Prop({ required: true })
  readonly table!: Vue

  get minFields () {
    return this.value.type === 'bayfill'
      ? 3
      : 2
  }
}
</script>

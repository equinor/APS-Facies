<template>
  <v-layout column>
    <h3>Alpha selection</h3>
    <v-layout row>
      <alpha-fields
        :value="value"
        :min-fields="minFields"
      />
    </v-layout>
    <h3>Truncation rule specification background facies</h3>
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
  </v-layout>
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

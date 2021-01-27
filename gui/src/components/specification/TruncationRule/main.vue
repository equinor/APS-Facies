<template>
  <v-row
    no-gutters
  >
    <h3>Alpha selection</h3>
    <alpha-fields
      :value="value"
      :min-fields="minFields"
    />
    <h3>Truncation rule specification background facies</h3>
    <v-row
      no-gutters
    >
      <v-col>
        <v-row
          no-gutters
        >
          <v-col>
            <component
              :is="table"
              :value="value"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-row>
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

  get minFields (): number {
    return this.value.type === 'bayfill'
      ? 3
      : 2
  }
}
</script>

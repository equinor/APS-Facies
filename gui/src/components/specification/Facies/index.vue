<template>
  <facies-specification-base
    :value="value.facies"
    :disable="disable"
    :clearable="clearable"
    @input.capture="(facies) => updateFacies(facies)"
  />
</template>

<script
  setup
  lang="ts"
  generic="
    T extends Polygon = Polygon,
    S extends PolygonSerialization = PolygonSerialization,
    P extends PolygonSpecification = PolygonSpecification,
"
>
import { ID } from '@/utils/domain/types'
import Facies from '@/utils/domain/facies/local'
import Polygon, {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import FaciesSpecificationBase from './base.vue'
import { useStore } from '../../../store'

type Props = {
  value: Polygon
  rule: TruncationRule<T, S, P>
  clearable: boolean
  disable: boolean | ((facies: Facies) => boolean)
}
const props = withDefaults(defineProps<Props>(), {
  clearable: false,
  disable: false,
})
const store = useStore()

async function updateFacies(faciesId: ID | undefined): Promise<void> {
  const facies = store.getters['facies/byId'](faciesId)
  await store.dispatch('truncationRules/updateFacies', {
    rule: props.rule,
    polygon: props.value,
    facies,
  })
}
</script>

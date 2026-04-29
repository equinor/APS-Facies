<template>
  <v-row class="ma-0 pa-0 shrink" align="center" justify="center">
    <svg
      :width="expand ? '100%' : DEFAULT_SIZE.width"
      :height="expand ? '100%' : DEFAULT_SIZE.height"
      viewBox="0 0 1 1"
      preserveAspectRatio="xMidYMid meet"
      :style="{
        opacity,
        display: 'block',
        maxWidth: '100%',
        maxHeight: '100%',
      }"
    >
      <!--
        `plotify` produces paths and annotations in math/plotly
        coordinates (y axis pointing upwards, on the unit square 0..1).
        Since SVG's y axis points downwards, we flip the shape group
        while keeping the labels in unflipped coordinates (using
        `y => 1 - y`) so that the text is not mirrored.
      -->
      <g transform="translate(0 1) scale(1 -1)">
        <path
          v-for="(polygon, i) in data.polygons"
          :key="`polygon-${i}`"
          :d="polygon.path"
          :fill="polygon.fillcolor"
          :stroke="polygon.line.color"
          stroke-width="1"
          stroke-linejoin="round"
          vector-effect="non-scaling-stroke"
        />
      </g>
      <text
        v-for="(annotation, i) in data.annotations"
        :key="`annotation-${i}`"
        :x="annotation.x"
        :y="1 - annotation.y"
        :fill="annotation.font.color"
        text-anchor="middle"
        dominant-baseline="central"
        font-family="Roboto, sans-serif"
        font-size="0.07"
        :transform="`rotate(${(annotation.angle * 180) / Math.PI} ${annotation.x} ${1 - annotation.y})`"
      >
        {{ annotation.text }}
      </text>
    </svg>
  </v-row>
</template>

<script
  setup
  lang="ts"
  generic="
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends TruncationRule<T, S, P>
  "
>
import rms from '@/api/rms'

import { DEFAULT_SIZE } from '@/config'
import { makeTruncationRuleSpecification } from '@/utils'
import { getDisabledOpacity } from '@/utils/helpers/simple'
import { plotify } from '@/utils/plotting'
import type { PlotSpecification } from '@/utils/plotting'
import { computed, ref, watch } from 'vue'
import type { TruncationRule } from '@/utils/domain/truncationRule'
import type { Polygon } from '@/utils/domain'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import { useGlobalFaciesStore } from '@/stores/facies/global'
import { useTruncationRuleStore } from '@/stores/truncation-rules'

type Props = {
  value: RULE
  expand?: boolean
}
const props = withDefaults(defineProps<Props>(), { expand: false })
const faciesGlobalStore = useGlobalFaciesStore()
const ruleStore = useTruncationRuleStore()

const data = ref<PlotSpecification>({
  polygons: [],
  annotations: [],
})
const disabled = ref(false)
const opacity = computed((): number => getDisabledOpacity(disabled.value))

watch(
  [
    () => props.value,
    // Vue struggles with changes in class properties
    () => props.value.facies,
    () =>
      props.value.polygons.map((polygon) => polygon.facies?.previewProbability),
  ],
  async () => {
    if (ruleStore.ready(props.value)) {
      disabled.value = false
      data.value = plotify(
        await rms.truncationPolygons(
          makeTruncationRuleSpecification(props.value),
        ),
        faciesGlobalStore.selected,
      )
    } else {
      disabled.value = true
    }
  },
  {
    deep: true,
    immediate: true,
  },
)
</script>

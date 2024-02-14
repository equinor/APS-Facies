<template>
  <static-plot
    :data-definition="__data.polygons"
    :annotations="__data.annotations"
    :width="300"
    :height="300"
    :max-height="maxSize.height"
    :max-width="maxSize.width"
    expand
    svg
    @click.native="clicked"
    ref="plot"
  />
</template>

<script setup lang="ts">
import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import type { ID } from '@/utils/domain/types'
import type { Cubic } from '@/utils/domain'
import type CubicPolygon from '@/utils/domain/polygon/cubic'
import type { PolygonDescription } from '@/api/types'

import { getId, makeSimplifiedTruncationRuleSpecification } from '@/utils'
import type { PlotSpecification } from '@/utils/plotting'
import { plotify } from '@/utils/plotting'
import { ref, computed } from 'vue'
import { useTheme } from 'vuetify'

interface BoundingBox {
  minX: number
  minY: number
  maxX: number
  maxY: number
}

type Props = {
  modelValue: CubicPolygon[]
  rule: Cubic
}
const props = defineProps<Props>()
const emit = defineEmits<{
  (event: 'update:model-value', value: CubicPolygon[]): void
}>()

const plot = ref<InstanceType<typeof StaticPlot> | null>(null)
const polygons = ref<PolygonDescription[]>([])

const maxSize = { width: 400, height: 400 }

const theme = useTheme()

const __data = computed<PlotSpecification>(() =>
  plotify(
    [
      ...polygons.value,
    ] /* Necessary to copy the array, as to not sort it in-place */
      .sort((a, b) => {
        const selected = props.modelValue.map(getId)
        if (!selected.includes(a.name) && !selected.includes(b.name)) return 0
        return (
          Number(selected.includes(a.name)) - Number(selected.includes(b.name))
        )
      }),
    props.rule.backgroundPolygons.map((polygon) => {
      return {
        name: polygon.id,
        color: has(polygon)
          ? (theme.global.current.value.colors.primary as string)
          : '#000',
        alias: polygon.level.filter((lvl) => lvl !== 0).join('.'),
      }
    }),
    '#fff',
  ),
)
const boundingBoxes = computed<{ name: string; boundingBox: BoundingBox }[]>(
  () =>
    polygons.value.map(({ name, polygon }) => ({
      name,
      boundingBox: polygon.reduce(
        (box, [x, y]) => {
          box.minX = Math.min(box.minX, x)
          box.maxX = Math.max(box.maxX, x)
          box.minY = Math.min(box.minY, 1 - y)
          box.maxY = Math.max(box.maxY, 1 - y)
          return box
        },
        {
          minX: Number.POSITIVE_INFINITY,
          maxX: Number.NEGATIVE_INFINITY,
          minY: Number.POSITIVE_INFINITY,
          maxY: Number.NEGATIVE_INFINITY,
        },
      ),
    })),
)

watch(
  props.rule,
  async () => {
    try {
      const newPolygons = await rms.truncationPolygons(
        makeSimplifiedTruncationRuleSpecification(props.rule),
      )
      polygons.value = newPolygons
    } catch (e) {
      // Ignore, as a cubic truncation rule may be inconsistent during an (vuex) action
    }
  },
  { deep: true, immediate: true },
)

function clicked(e: MouseEvent): void {
  const { x, y } = relativeClickPosition(e)
  const { name } = boundingBoxes.value.find(
    ({ boundingBox }) =>
      boundingBox.minX <= x &&
      x <= boundingBox.maxX &&
      boundingBox.minY <= y &&
      y <= boundingBox.maxY,
  ) || { name: undefined }
  if (name === undefined) {
    emit('update:model-value', props.modelValue)
  } else if (has(name)) {
    emit(
      'update:model-value',
      props.modelValue.filter((item) => getId(item) !== name),
    )
  } else {
    emit('update:model-value', [
      ...props.modelValue,
      props.rule.polygons.find(
        (polygon) => getId(polygon) === name,
      ) as CubicPolygon,
    ])
  }
}

function relativeClickPosition(e: MouseEvent): { x: number; y: number } {
  const element = plot.value!.$el as HTMLElement
  const { top, bottom, left, right } = element
    .getElementsByClassName('svg-container')[0]
    .getBoundingClientRect()
  const getMax = (direction: 'X' | 'Y'): number =>
    Math.max(
      ...boundingBoxes.value.map(
        ({ boundingBox }) => boundingBox[`max${direction}`],
      ),
    )
  return {
    x: Math.min((e.clientX - left) / (right - left), getMax('X')),
    y: Math.min((e.clientY - top) / (bottom - top), getMax('Y')),
  }
}

function has(item: CubicPolygon | ID | undefined): boolean {
  return props.modelValue.map(getId).includes(getId(item))
}
</script>

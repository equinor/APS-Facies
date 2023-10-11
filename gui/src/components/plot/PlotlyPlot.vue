<template>
  <div ref="plot" class="vue-plotly" />
</template>
<script setup lang="ts">
import Plotly, { Config, Layout, PlotData, PlotlyHTMLElement } from 'plotly.js'
import debounce from 'lodash/debounce'
import { ref } from 'vue'
import { onMounted } from 'vue'
import { computed } from 'vue'

// TODO: implement more if we need it

type Props = {
  autoResize: boolean
  options: Partial<Config>
  data: Partial<PlotData>[]
  layout: Partial<Layout>
  watchShallow?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  watchShallow: false,
})

const plot = ref<PlotlyHTMLElement | null>(null)
const resizeListener = ref<EventListener | null>(null)
// const clickListener = ref((event: PlotMouseEvent) => emit('click', event))

const dataRevision = ref(1)

const internalLayout = computed<Partial<Layout>>(() => ({
  ...props.layout,
  datarevision: dataRevision.value,
}))

function initEvents() {
  if (props.autoResize) {
    resizeListener.value = () => {
      dataRevision.value++
      debounce(react, 200) // TODO: THIS DOES NOTHING, RIGHT?
    }
    window.addEventListener('resize', resizeListener.value)
  }
  // container.value!.on('plotly_click', clickListener.value)
}

function getOptions(): Partial<Config> {
  const el = plot.value!
  let options = props.options ?? {}

  // if width/height is not specified for toImageButton, default to el.clientWidth/clientHeight
  options.toImageButtonOptions = options.toImageButtonOptions ?? {}
  options.toImageButtonOptions.width =
    options.toImageButtonOptions.width ?? el.clientWidth
  options.toImageButtonOptions.height =
    options.toImageButtonOptions.height ?? el.clientHeight
  return options
}

// weird plotly term for "redraw"
async function react() {
  plot.value = await Plotly.react(
    plot.value!,
    props.data,
    internalLayout.value,
    getOptions(),
  )
}

onMounted(() => {
  react()
  initEvents()
})

defineExpose({ plot, react })
</script>
<style></style>

<!--
Credit to Aurélio A. Heckert; https://github.com/aurium
Adjusted from https://github.com/aurium/vue-plotly/blob/master/src/components/Plotly.vue
to fit what we originally had
Originally licensed under MIT
-->
<template>
  <div :id="id" ref="plot" />
</template>
<script setup lang="ts">
import type {
  PropType,
} from 'vue'
import {
  ref,
  onMounted,
  onBeforeUnmount,
  onUpdated,
  getCurrentInstance,
  watch,
  nextTick,
  useAttrs,
} from 'vue'
import type { PlotlyHTMLElement, Data, Layout } from 'plotly.js-dist-min'
import Plotly from 'plotly.js-dist-min'
import events from './events'
import { camelize } from './utils/helper'
import { useResizeObserver } from '@vueuse/core'
import { cloneDeep, isEqual } from 'lodash'

const instance = getCurrentInstance()
if (!instance) throw Error('Bad component initialization')

const plot = ref<PlotlyHTMLElement>({} as PlotlyHTMLElement)

defineExpose({ plot })
defineEmits(events.map(e => e.eventName))

type Scheduled = { replot: boolean }
const scheduled = ref<null | Scheduled>(null)

const props = defineProps({
  data: Array as PropType<Data[]>,
  layout: Object as PropType<Partial<Layout>>,
  id: {
    type: String,
    required: false,
    default: null
  }
})

const innerLayout = ref<Partial<Plotly.Layout>>({ ...props.layout })

const throttleDelay = 100
let lastResize = 0 // Timestamp

const onResize = ()=> {
  const next = lastResize + throttleDelay - Date.now()
  if (next <= 0) doResize()
  else setTimeout(doResize, next)
}

const doResize = ()=> {
  lastResize = Date.now()
  Plotly.Plots.resize(plot.value)
}

// Hey, attrs are not reactve. Sorry.
const getOptions = ()=> {
  const attrs = useAttrs()
  const optionsFromAttrs = Object.keys(attrs).reduce((acc, key) => {
    acc[camelize(key)] = attrs[key]
    return acc
  }, {} as Record<string, unknown>) as Record<string, unknown>
  return {
    responsive: false,
    staticPlot: true,
    ...optionsFromAttrs,
    displayModeBar: false,
    displaylogo: false,
  } as Partial<Plotly.Config>
}

const options = ref<Partial<Plotly.Config>>(getOptions())

onMounted(()=> {
  Plotly.newPlot(plot.value, props.data || [], innerLayout.value, options.value)
  events.forEach(evt => {
    if (!plot.value) return
    plot.value.on(evt.eventName, evt.handler(instance))
  })
  useResizeObserver(plot, onResize)
})

onBeforeUnmount(()=> {
  events.forEach(event => {
    if (!plot.value) return
    plot.value.removeAllListeners(event.eventName)
  })
  Plotly.purge(plot.value)
})

// watch for attrs or a computed based on that wont work.
// "the attrs object here always reflects the latest fallthrough attributes,
// it isn't reactive [...] you can use onUpdated()."
// https://vuejs.org/guide/components/attrs.html#accessing-fallthrough-attributes-in-javascript
onUpdated(()=> {
  const updatedOpts = getOptions()
  if (!isEqual(options.value, updatedOpts)) {
    options.value = updatedOpts
    schedule({ replot: true })
  }
})

watch(() => props.data,
  ()=> schedule({ replot: true }),
  { deep: true }
)

watch(() => props.layout,
  () => {
    innerLayout.value = cloneDeep(props.layout!)
    schedule({ replot: false })
  }
)

function schedule(context: Scheduled) {
  if (scheduled.value) {
    (scheduled.value as Scheduled).replot = (scheduled.value as Scheduled).replot || context.replot
    return
  }
  scheduled.value = context
  nextTick(() => {
    const replot = scheduled.value?.replot
    scheduled.value = null
    if (replot) {
      react()
      return
    }
    if ((innerLayout.value.height ?? 0) > 0) {
      Plotly.relayout(plot.value, innerLayout.value)
    }
  })
}

function react() {
  Plotly.react(plot.value, props.data || [], innerLayout.value, options.value)
}
</script>

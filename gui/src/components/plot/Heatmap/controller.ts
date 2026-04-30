import {
  DatasetController,
  Element,
  type ChartDataset,
  type UpdateMode,
} from 'chart.js'

import type { ColorScale } from '../utils'
import {scales as NAMED_SCALES, defaultScale} from './scales.ts'

/* ------------------------------------------------------------------ *
 * Chart.js module augmentation                                       *
 *                                                                    *
 * This is the official way to register a new chart type with         *
 * Chart.js: extend ChartTypeRegistry with the type's metadata so     *
 * that `type: 'heatmap'` becomes a valid, fully-typed chart type.    *
 * ------------------------------------------------------------------ */

export interface HeatmapDatasetOptions {
  /** Optional named or stop-array color scale (see ../utils). */
  colorScale?: ColorScale
  /**
   * Bilinear smoothing between cells, equivalent to Plotly's
   * `zsmooth: 'best'`.  When enabled (default), the grid is rendered to
   * an offscreen canvas at native resolution (cols × rows) and scaled
   * with `imageSmoothingQuality = 'high'`.  Set to false for crisp,
   * un-smoothed cell boundaries (Plotly's `zsmooth: false`).
   */
  smooth?: boolean
}

export interface HeatmapParsedData {
  x: number
  y: number
  v: number
}

declare module 'chart.js' {
  interface ChartTypeRegistry {
    heatmap: {
      chartOptions: unknown
      datasetOptions: HeatmapDatasetOptions
      // A "data point" in the public API is a row of the grid.
      defaultDataPoint: number[]
      metaExtensions: object
      parsedDataType: HeatmapParsedData
      scales: 'x' | 'y'
    }
  }
}

interface HeatmapCellProps {
  x: number
  y: number
  width: number
  height: number
  color: string
}

/* ------------------------------------------------------------------ *
 * Element                                                            *
 * ------------------------------------------------------------------ */

export class HeatmapCellElement extends Element<HeatmapCellProps> {
  static id = 'heatmapCell'
  static defaults = {}

  // Per-cell drawing is delegated to HeatmapController.draw, which paints
  // the whole grid in one pass via an offscreen canvas (so we can apply
  // bilinear smoothing).  This element exists only to satisfy Chart.js'
  // controller/element machinery and to expose hit-testing hooks for
  // future tooltip integration.
  draw(): void {
    /* no-op */
  }

  inRange(): boolean {
    return false
  }
  inXRange(): boolean {
    return false
  }
  inYRange(): boolean {
    return false
  }
  getCenterPoint(): { x: number; y: number } {
    const { x, y, width, height } = this as unknown as HeatmapCellProps
    return { x: x + width / 2, y: y + height / 2 }
  }
  getRange(): number {
    return 0
  }
}

/* ------------------------------------------------------------------ *
 * Controller                                                         *
 * ------------------------------------------------------------------ */

export class HeatmapController extends DatasetController<'heatmap'> {
  static readonly id = 'heatmap'

  /** Reusable offscreen buffer holding one pixel per grid cell. */
  private _imageBuffer: HTMLCanvasElement | null = null
  private _imageBufferCtx: CanvasRenderingContext2D | null = null

  static readonly defaults = {
    dataElementType: HeatmapCellElement.id,
    animation: false,
    animations: {},
    transitions: {
      active: { animation: { duration: 0 } },
      resize: { animation: { duration: 0 } },
      show: { animation: { duration: 0 } },
      hide: { animation: { duration: 0 } },
    },
    datasets: { animation: false },
  }

  static readonly overrides = {
    aspectRatio: 1,
    animation: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
    },
    scales: {
      x: { type: 'linear', display: false, min: 0, offset: false },
      y: {
        type: 'linear',
        display: false,
        min: 0,
        offset: false,
        reverse: true,
      },
    },
  }

  initialize(): void {
    this.enableOptionSharing = true
    super.initialize()
  }

  /**
   * Replace the default array-length sync (which would see only rows)
   * with a flat synthetic array of length rows * cols so that one
   * element is created per cell.
   */
  _dataCheck(): void {
    const grid = this._grid()
    const rows = grid.length
    const cols = rows && grid[0] ? grid[0].length : 0
    // Replace _data with a synthetic flat array – its length is what
    // _resyncElements uses to size the cell-element array.
    ;(this as unknown as { _data: unknown[] })._data = new Array(rows * cols)
  }

  parse(start: number, count: number): void {
    const meta = this._cachedMeta as unknown as {
      _parsed: { x: number; y: number; v: number }[]
      _sorted: boolean
    }
    const grid = this._grid()
    const cols = grid[0]?.length ?? 0
    const parsed = meta._parsed ?? (meta._parsed = [])
    for (let i = 0; i < count; i++) {
      const idx = start + i
      const r = cols > 0 ? Math.floor(idx / cols) : 0
      const c = cols > 0 ? idx % cols : 0
      parsed[idx] = { x: c, y: r, v: grid[r]?.[c] ?? 0 }
    }
    meta._sorted = true
  }

  /**
   * Inform the scales of the data extents so axes auto-range correctly.
   */
  getMinMax(): { min: number; max: number } {
    const grid = this._grid()
    const rows = grid.length
    const cols = rows && grid[0] ? grid[0].length : 0
    return { min: 0, max: Math.max(rows, cols) }
  }

  update(mode: UpdateMode): void {
    const elements = (this._cachedMeta.data ?? []) as HeatmapCellElement[]
    this.updateElements(elements, 0, elements.length, mode)
  }

  updateElements(
    elements: HeatmapCellElement[],
    start: number,
    count: number,
    mode: UpdateMode,
  ): void {
    // Element props are not used for rendering (controller.draw paints
    // the entire grid in one pass), but we still call updateElement so
    // that Chart.js' element bookkeeping stays consistent.
    if (!elements.length) return
    for (let i = 0; i < count; i++) {
      const idx = start + i
      const element = elements[i]
      if (element === undefined) continue
      this.updateElement(
        element,
        idx,
        { x: 0, y: 0, width: 0, height: 0, color: '#000' } as unknown as Record<
          string,
          unknown
        >,
        mode,
      )
    }
  }

  /**
   * Render the entire heatmap.
   *
   * Strategy: paint one pixel per cell into a (cols × rows) offscreen
   * canvas, then blit it scaled to the chart area.  When `smooth` is
   * enabled (default), the browser's native bilinear filter does the
   * up-sampling — this is the same approach Plotly uses for
   * `zsmooth: 'best'`.
   */
  draw(): void {
    const dataset = this.getDataset() as unknown as ChartDataset<'heatmap'>
    const grid = (dataset.data ?? []) as number[][]
    const rows = grid.length
    const cols = rows && grid[0] ? grid[0].length : 0
    if (!rows || !cols) return

    const xScale = this._cachedMeta.xScale
    const yScale = this._cachedMeta.yScale
    if (!xScale || !yScale) return

    const xStart = xScale.getPixelForValue(0)
    const xEnd = xScale.getPixelForValue(cols)
    const yStart = yScale.getPixelForValue(0)
    const yEnd = yScale.getPixelForValue(rows)
    const dx = Math.min(xStart, xEnd)
    const dy = Math.min(yStart, yEnd)
    const dw = Math.abs(xEnd - xStart)
    const dh = Math.abs(yEnd - yStart)
    if (dw <= 0 || dh <= 0) return

    const buffer = this._ensureBuffer(cols, rows)
    const bufCtx = this._imageBufferCtx
    if (!buffer || !bufCtx) return

    const { min, max } = computeValueRange(grid)
    const range = max - min || 1
    const getColor = makeColorGetter(
      (dataset.colorScale ?? 'Greys') as ColorScale,
    )

    // Fill the buffer one pixel per cell.
    const image = bufCtx.createImageData(cols, rows)
    const pixels = image.data
    for (let r = 0; r < rows; r++) {
      const row = grid[r]
      if (!row) continue
      for (let c = 0; c < cols; c++) {
        const t = ((row[c] ?? 0) - min) / range
        const [pr, pg, pb] = parseColor(getColor(t))
        const offset = (r * cols + c) * 4
        pixels[offset] = pr
        pixels[offset + 1] = pg
        pixels[offset + 2] = pb
        pixels[offset + 3] = 255
      }
    }
    bufCtx.putImageData(image, 0, 0)

    const ctx = this.chart.ctx
    const smooth = dataset.smooth !== false

    ctx.save()
    // Clip to the chart area so the blit can't bleed onto axes.
    const area = this.chart.chartArea
    ctx.beginPath()
    ctx.rect(area.left, area.top, area.right - area.left, area.bottom - area.top)
    ctx.clip()

    ctx.imageSmoothingEnabled = smooth
    if (smooth) {
      // 'high' triggers bilinear/bicubic in modern browsers, matching
      // Plotly's 'best' setting.
      ctx.imageSmoothingQuality = 'high'
    }
    ctx.drawImage(buffer, dx, dy, dw, dh)
    ctx.restore()
  }

  private _ensureBuffer(
    cols: number,
    rows: number,
  ): HTMLCanvasElement | null {
    if (cols <= 0 || rows <= 0) return null
    let buffer = this._imageBuffer
    if (!buffer) {
      buffer = document.createElement('canvas')
      this._imageBuffer = buffer
    }
    if (buffer.width !== cols) buffer.width = cols
    if (buffer.height !== rows) buffer.height = rows
    if (!this._imageBufferCtx) {
      this._imageBufferCtx = buffer.getContext('2d', { willReadFrequently: true })
    }
    return buffer
  }

  private _grid(): number[][] {
    const data = this.getDataset().data as unknown as
      | number[][]
      | null
      | undefined
    return Array.isArray(data) ? data : []
  }
}

/* ------------------------------------------------------------------ *
 * Color resolution                                                   *
 * ------------------------------------------------------------------ */

function computeValueRange(grid: number[][]): { min: number; max: number } {
  let min = Number.POSITIVE_INFINITY
  let max = Number.NEGATIVE_INFINITY
  for (const row of grid) {
    for (const v of row) {
      if (v < min) min = v
      if (v > max) max = v
    }
  }
  if (!isFinite(min)) {
    min = 0
    max = 1
  }
  return { min, max }
}


type Stops = readonly (readonly [number, string])[]

function resolveStops(scale: ColorScale): Stops {
  if (typeof scale === 'string') {
    return NAMED_SCALES[scale] ?? defaultScale
  }
  if (Array.isArray(scale) && scale.length > 0) {
    const denom = Math.max(scale.length - 1, 1)
    return scale.map(
      (s, i) => [i / denom, s.color] as [number, string],
    )
  }
  return defaultScale
}

function makeColorGetter(scale: ColorScale): (t: number) => string {
  const stops = resolveStops(scale)
  return (t) => interpolateStops(stops, clamp01(t))
}

function clamp01(t: number): number {
  if (t < 0) return 0
  if (t > 1) return 1
  return Number.isFinite(t) ? t : 0
}

function interpolateStops(stops: Stops, t: number): string {
  const first = stops[0]
  const last = stops[stops.length - 1]
  if (!first || !last) return '#000000'
  if (stops.length === 1) return first[1]
  for (let i = 1; i < stops.length; i++) {
    const lo = stops[i - 1]
    const hi = stops[i]
    if (!lo || !hi) continue
    if (t <= hi[0]) {
      const k = (t - lo[0]) / Math.max(hi[0] - lo[0], 1e-9)
      return mixHex(lo[1], hi[1], k)
    }
  }
  return last[1]
}

function mixHex(a: string, b: string, t: number): string {
  const ca = parseColor(a)
  const cb = parseColor(b)
  const r = Math.round(ca[0] + (cb[0] - ca[0]) * t)
  const g = Math.round(ca[1] + (cb[1] - ca[1]) * t)
  const bl = Math.round(ca[2] + (cb[2] - ca[2]) * t)
  return `rgb(${r},${g},${bl})`
}

function parseHex(c: string): [number, number, number] {
  // Accepts #rgb / #rrggbb.  Falls back to black on unexpected input.
  if (c.startsWith('#')) {
    const hex = c.slice(1)
    if (hex.length === 3) {
      const r = hex[0] ?? '0'
      const g = hex[1] ?? '0'
      const b = hex[2] ?? '0'
      return [
        parseInt(r + r, 16),
        parseInt(g + g, 16),
        parseInt(b + b, 16),
      ]
    }
    if (hex.length === 6) {
      return [
        parseInt(hex.slice(0, 2), 16),
        parseInt(hex.slice(2, 4), 16),
        parseInt(hex.slice(4, 6), 16),
      ]
    }
  }
  return [0, 0, 0]
}

/**
 * Parse the strings produced by makeColorGetter — either `#rgb`/`#rrggbb`
 * (raw color stop) or `rgb(r,g,b)` (interpolated mix).
 */
function parseColor(c: string): [number, number, number] {
  if (c.startsWith('#')) return parseHex(c)
  const m = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/.exec(c)
  if (m) {
    return [
      Number.parseInt(m[1] ?? '0', 10),
      Number.parseInt(m[2] ?? '0', 10),
      Number.parseInt(m[3] ?? '0', 10),
    ]
  }
  return [0, 0, 0]
}

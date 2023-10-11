import hexRgb from 'hex-rgb'

import APSTypeError from '@/utils/domain/errors/type'
import { Color } from '@/utils/domain/facies/helpers/colors'
import colors from 'vuetify/util/colors'

import { PolygonDescription } from '@/api/types'

function svgPoint(point: [number, number], width = 1, height = 1): string {
  return `${point[0] * width},${point[1] * height}`
}

function polygon2svg(
  polygon: [number, number][],
  width = 1,
  height = 1,
): string {
  return polygon
    .reduce(
      (path, point): string =>
        path.concat(` L ${svgPoint(point, width, height)}`),
      `M ${svgPoint(polygon[0], width, height)}`,
    )
    .concat(' Z')
}

function average(arr: number[]): number {
  return arr.reduce((sum, e): number => sum + e, 0) / arr.length
}

function centerOfPolygon(polygon: [number, number][]): {
  x: number
  y: number
} {
  const points = polygon.reduce(
    (point, [x, y]) => {
      point.x.push(x)
      point.y.push(y)
      return point
    },
    {
      x: [] as number[],
      y: [] as number[],
    },
  )
  return {
    x: average(points.x),
    y: average(points.y),
  }
}

interface RGB {
  red: number
  green: number
  blue: number
}

function toRgb(color: string): RGB {
  if (/^#?[0-9a-f]{3,6}$/.test(color)) {
    return hexRgb(color)
  }
  const match = /^rgb\((\d+), (\d+), (\d+)\)$/.exec(color)
  if (!match || match.length !== 4)
    throw new APSTypeError(`The given color, ${color}, is not valid`)
  return {
    red: Number(match[1]),
    green: Number(match[2]),
    blue: Number(match[3]),
  }
}

function luminance({ red, green, blue }: RGB): number {
  /* Borrowed from https://stackoverflow.com/questions/9733288/how-to-programmatically-calculate-the-contrast-ratio-between-two-colors
   * */
  const [x, y, z] = [red, green, blue].map((v) => {
    v /= 255
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * x + 0.7152 * y + 0.0722 * z
}

function contrast(color: string, other: string): number {
  const l1 = luminance(toRgb(color)) + 0.05
  const l2 = luminance(toRgb(other)) + 0.05
  return Math.max(l1, l2) / Math.min(l1, l2)
}

function getTextColor(backgroundColor: string): string {
  const textColors = [colors.grey.darken3, colors.grey.lighten4]
  return textColors.reduce(
    (bestContrast, textColor) => {
      const _contrast = contrast(backgroundColor, textColor)
      if (bestContrast.contrast < _contrast) {
        return {
          contrast: _contrast,
          color: textColor,
        }
      } else {
        return bestContrast
      }
    },
    {
      color: '',
      contrast: 0,
    },
  ).color
}

interface PolygonSpecification {
  type: string
  path: string
  fillcolor: Color
  name: string
  line: {
    color: Color
  }
}

interface AnnotationSpecification {
  x: number
  y: number
  xref: string
  yref: string
  text: string
  font: {
    color: Color
  }
  showarrow: boolean
}

export interface PlotSpecification {
  polygons: PolygonSpecification[]
  annotations: AnnotationSpecification[]
}

type FaciesTable = { name: string; color: string; alias: string }[]

export function plotify(
  polygons: PolygonDescription[],
  faciesTable: FaciesTable,
  fillColor = '',
): PlotSpecification {
  return polygons.reduce(
    (obj, { name, polygon }): PlotSpecification => {
      const facies = faciesTable.find((facies): boolean => facies.name === name)
      if (!facies) {
        return obj
      }
      const color = facies.color

      // Add SVG polygon
      obj.polygons.push({
        type: 'path',
        path: polygon2svg(polygon),
        fillcolor: fillColor || color,
        name,
        line: {
          color,
        },
      })

      // Add alias to polygons
      const { x, y } = centerOfPolygon(polygon)
      obj.annotations.push({
        x,
        y,
        xref: 'x',
        yref: 'y',
        text: facies.alias,
        font: {
          color: getTextColor(fillColor || color),
        },
        showarrow: false,
      })

      return obj
    },
    {
      polygons: [] as PolygonSpecification[],
      annotations: [] as AnnotationSpecification[],
    },
  )
}

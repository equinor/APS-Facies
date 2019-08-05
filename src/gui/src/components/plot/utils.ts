import { Color } from '@/utils/domain/facies/helpers/colors'

export type ColorScale = string | { value: number, color: Color}[]

export function colorMapping (colorScale: ColorScale) {
  if (Array.isArray(colorScale)) {
    const colors = []
    for (const item of colorScale) {
      // Plot.ly does not offer an easier way of ensure the values are discrete
      colors.push([(item.value - 1) / colorScale.length, item.color])
      colors.push([item.value / colorScale.length, item.color])
    }
    return colors
  } else {
    return colorScale
  }
}

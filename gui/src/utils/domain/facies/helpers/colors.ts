import type { Branded } from '@/utils/typing/simple'

export type Color = Branded<string, 'color'> | 'primary' | 'black' | 'white'

export const apsColors: Color[] = [
  '#7cfc00', // lawngreen
  '#808080', // grey
  '#1e90ff', // dodgerblue
  '#ffd700', // gold
  '#9932cc', // darkorchid
  '#00ffff', // cyan
  '#b22222', // firebrick
  '#6b8e23', // olivedrab
  '#0000ff', // blue
  '#dc143c', // crimson
  '#ff8c00', // darkorange
  '#ff0000', // red
] as Color[]

export const generalColors: Color[] = [
  'rgb(222, 47, 16)',
  'rgb(229, 133, 30)',
  'rgb(238, 184, 42)',
  'rgb(245, 218, 50)',
  'rgb(220, 245, 55)',
  'rgb(158, 228, 49)',
  'rgb(89, 161, 163)',
  'rgb(114, 206, 43)',
  'rgb(61, 32, 180)',
  'rgb(43, 71, 178)',
  'rgb(200, 43, 82)',
  'rgb(163, 36, 172)',
] as Color[]

export const faciesColors: Color[] = [
  'rgb(241, 201, 46)',
  'rgb(252, 246, 136)',
  'rgb(182, 199, 64)',
  'rgb(162, 169, 45)',
  'rgb(83, 151, 88)',
  'rgb(129, 109, 27)',
  'rgb(64, 118, 162)',
  'rgb(70, 128, 195)',
  'rgb(29, 24, 66)',
  'rgb(92, 152, 204)',
  'rgb(81, 148, 191)',
  'rgb(113, 184, 195)',
  'rgb(209, 83, 44)',
  'rgb(73, 25, 95)',
  'rgb(229, 165, 37)',
  'rgb(1, 1, 1)',
  'rgb(139, 139, 139)',
] as Color[]

export const colorLibraries = {
  APS: apsColors,
  'General Colors': generalColors,
  Facies: faciesColors,
}

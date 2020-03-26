import { ID } from '@/utils/domain/types'

export interface CodeName {
  code: number
  name: string
}

export interface RmsFacies extends CodeName {
  observed: null | {
    zones: number[]
    regions: number[]
  }
}

export interface MinMax {
  min: number
  max: number
}

export interface Constants extends MinMax{
  tolerance: number
}

export interface SimulationBoxSize {
  size: {
    x: number
    y: number
    z: number
  }
  rotation: number
  origin: {
    x: number
    y: number
  }
}

export interface AverageParameterProbabilities {
  [parameter: string]: number
}

export interface PolygonDescription {
  name: ID
  polygon: [number, number][]
}

export interface RmsGridModel {
  name: string
  exists: boolean
  zones: number
  hasDualIndexSystem: boolean
}

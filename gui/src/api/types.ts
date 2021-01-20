import { ID } from '@/utils/domain/types'

export interface CodeName {
  code: number
  name: string
}

export interface Paths {
  model: string
  fmuConfig: string | null
  probabilityDistribution: string | null
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

export interface Job {
  id: string
  instance_name: string
  'uncertain.size': number
  elapsedrealtime: number
  elapsedcputime: number
  tableoffset: number
  surfreprfloat: boolean
  'description.size': number
  opentime: Date
  identifier: number
  changeuser: string
  changetime: Date
  jobinputjson: string
  pluginname: string
  plugindescription: string
  pluginauthor: string
  treeorigin: string
}

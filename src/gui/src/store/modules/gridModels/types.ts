export type GridModel = string

export interface GridModelsState {
  available: GridModel[]
  current: GridModel | null
}

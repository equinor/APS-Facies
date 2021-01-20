import { ItemsState } from '@/utils/domain/bases/baseItem'
import GridModel from '@/utils/domain/gridModel'
import { ID } from '@/utils/domain/types'

export interface GridModelsState extends ItemsState<GridModel> {
  current: ID | null
}

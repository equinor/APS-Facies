import { ID } from '@/utils/domain/types'

export interface PolygonDescription {
  name: ID
  polygon: [number, number][]
}

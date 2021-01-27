import { Optional } from '@/utils/typing'

export interface SimulationBoxState {
  size: {
    x: Optional<number>
    y: Optional<number>
    z: Optional<number>
  }
  origin: {
    x: Optional<number>
    y: Optional<number>
  }
}

export default interface GridParameterState {
  _waiting: boolean
  azimuth: Optional<number>
  size: {
    x: Optional<number>
    y: Optional<number>
    z: Optional<number>
  }
  simBox: SimulationBoxState
}

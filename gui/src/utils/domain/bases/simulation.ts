import { ZoneRegionDependent } from '@/utils/domain/bases/index'
import type {
  DependentConfiguration,
  DependentSerialization,
} from '@/utils/domain/bases/zoneRegionDependent'

export type SimulationConfiguration = DependentConfiguration & {
  simulation?: number[][] | null
  _dataHash?: string
}

export interface SimulationSerialization extends DependentSerialization {
  simulation: number[][] | null
  _dataHash: string
}

export default abstract class Simulation extends ZoneRegionDependent {
  protected _simulation: number[][] | null
  private _dataHash: string

  protected constructor({
    simulation = null,
    _dataHash = '',
    ...rest
  }: SimulationConfiguration) {
    super(rest)

    this._simulation = simulation
    this._dataHash = _dataHash
    this._excludeFromHash.push(...['_dataHash', 'simulation'])
  }

  public get simulated(): boolean {
    return this._simulation
      ? this._simulation.length > 0 && this._simulation[0].length > 0
      : false
  }

  protected get simulation(): number[][] | null {
    return this._simulation
  }

  protected set simulation(data) {
    this._simulation = data
    this._dataHash = this.hash
  }

  public get isRepresentative(): boolean {
    return this._dataHash === this.hash
  }

  protected toJSON(): SimulationSerialization {
    return {
      ...super.toJSON(),
      simulation: this.simulation,
      _dataHash: this._dataHash,
    }
  }
}

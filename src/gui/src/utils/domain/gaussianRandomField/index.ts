import CrossSection, {
  CrossSectionSerialization
} from '@/utils/domain/gaussianRandomField/crossSection'
import cloneDeep from 'lodash/cloneDeep'

import { newSeed } from '@/utils/helpers'
import { Named } from '@/utils/domain/bases/interfaces'
import { Parent } from '@/utils/domain'
import Simulation, {
  SimulationConfiguration,
  SimulationSerialization,
} from '@/utils/domain/bases/simulation'

import Trend, { TrendSerialization } from '@/utils/domain/gaussianRandomField/trend'
import Variogram, { VariogramSerialization } from '@/utils/domain/gaussianRandomField/variogram'

interface Settings {
  crossSection: CrossSection
  gridModel: {
    use: boolean
    size: {
      x: number
      y: number
      z: number
    }
  }
  seed: number
}

interface SettingsSerialization {
  crossSection: CrossSectionSerialization
  gridModel: {
    use: boolean
    size: {
      x: number
      y: number
      z: number
    }
  }
  seed: number
}

function defaultSettings (parent: Parent): Settings {
  return {
    crossSection: new CrossSection({
      type: 'IJ',
      parent,
    }),
    gridModel: {
      use: false,
      size: {
        x: 100, y: 100, z: 1,
      },
    },
    seed: newSeed(),
  }
}

export type GaussianRandomFieldConfiguration = SimulationConfiguration & {
  name: string
  overlay?: boolean
  channel?: number | null
  variogram?: Variogram | null
  trend?: Trend | null
  settings?: Settings | null
  crossSection?: CrossSection | null
  seed?: number | null
}

export interface GaussianRandomFieldSpecification {
  name: string
  settings: Settings
  trend: Trend
  variogram: Variogram
}

export interface GaussianRandomFieldSerialization extends SimulationSerialization {
  name: string
  settings: SettingsSerialization
  trend: TrendSerialization
  variogram: VariogramSerialization
}

export default class GaussianRandomField extends Simulation implements Named {
  public name: string
  public variogram: Variogram
  public trend: Trend
  public settings: Settings
  public waiting: boolean

  public valid: boolean

  public constructor ({ name, variogram = null, trend = null, settings = null, crossSection = null, seed = null, ...rest }: GaussianRandomFieldConfiguration) {
    super(rest)
    this.name = name
    this.variogram = variogram || new Variogram({})
    this.trend = trend || new Trend({})
    this.settings = settings || defaultSettings(this.parent)
    if (crossSection) {
      this.settings.crossSection = crossSection
    }
    if (seed && seed >= 0) {
      this.settings.seed = seed
    }
    // TODO: Make sure the class knows that the data is actually from the CURRENT specification
    //   E.g. use a hash of the specification (variogram, trend, and settings)
    this.waiting = false
    this.valid = true
  }

  public get simulation (): number[][] | null { return super.simulation }
  public set simulation (data) { super.simulation = data }

  public get isFmuUpdatable (): boolean {
    return this.variogram.isFmuUpdatable || (this.trend.use && this.trend.isFmuUpdatable)
  }

  public specification ({ rootGetters }: { rootGetters?: { simulationSettings: () => object } } = {}): GaussianRandomFieldSpecification {
    return {
      name: this.name,
      variogram: this.variogram,
      trend: this.trend,
      settings: {
        ...rootGetters ? cloneDeep(rootGetters.simulationSettings()) : {},
        ...this.settings,
      },
    }
  }

  public toJSON (): GaussianRandomFieldSerialization {
    return {
      ...super.toJSON(),
      name: this.name,
      settings: {
        crossSection: this.settings.crossSection.toJSON(),
        gridModel: { ...this.settings.gridModel },
        seed: this.settings.seed,
      },
      variogram: this.variogram.toJSON(),
      trend: this.trend.toJSON(),
    }
  }
}

export {
  Variogram,
  Trend,
  TrendSerialization,
  VariogramSerialization,
}

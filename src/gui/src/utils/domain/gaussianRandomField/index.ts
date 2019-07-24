import CrossSection, {
  CrossSectionSerialization
} from '@/utils/domain/gaussianRandomField/crossSection'
import cloneDeep from 'lodash/cloneDeep'

import { newSeed } from '@/utils/helpers'
import { Named, Parent } from '@/utils/domain/bases/interfaces'
import ZoneRegionDependent, {
  DependentConfiguration,
  DependentSerialization
} from '@/utils/domain/bases/zoneRegionDependent'

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
      relativePosition: 0.5,
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

export type GaussianRandomFieldConfiguration = DependentConfiguration & {
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

export interface GaussianRandomFieldSerialization extends DependentSerialization {
  name: string
  settings: SettingsSerialization
  trend: TrendSerialization
  variogram: VariogramSerialization
}

class GaussianRandomField extends ZoneRegionDependent implements Named {
  public name: string
  public variogram: Variogram
  public trend: Trend
  public settings: Settings
  public waiting: boolean

  private _data: number[][]

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
    this._data = []
  }

  public get simulated (): boolean {
    return this._data.length > 0 && this._data[0].length > 0
  }

  public get simulation (): number[][] {
    return this._data
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

export default GaussianRandomField

export {
  Variogram,
  Trend,
  GaussianRandomField,
  TrendSerialization,
  VariogramSerialization,
}

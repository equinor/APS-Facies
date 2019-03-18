import CrossSection, { CrossSectionConfiguration } from '@/utils/domain/gaussianRandomField/crossSection'
import cloneDeep from 'lodash/cloneDeep'

import { newSeed } from '@/utils/helpers'
import { Named, Parent } from '@/utils/domain/bases/interfaces'
import ZoneRegionDependent, { DependentConfiguration } from '@/utils/domain/bases/zoneRegionDependent'
import { Identified } from '@/utils/domain/types'

import Trend from '@/utils/domain/gaussianRandomField/trend'
import Variogram from '@/utils/domain/gaussianRandomField/variogram'

interface Settings {
  crossSection: CrossSectionConfiguration
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
}

interface GaussianRandomFieldSpecification {
  name: string
  settings: Settings
  trend: Trend
  variogram: Variogram
}

class GaussianRandomField extends ZoneRegionDependent implements Named {
  public name: string
  public variogram: Variogram
  public trend: Trend
  public settings: Settings
  public waiting: boolean

  private _data: number[][]

  public constructor ({ name, variogram = null, trend = null, settings = null, crossSection = null, ...rest }: GaussianRandomFieldConfiguration) {
    super(rest)
    this.name = name
    this.variogram = variogram || new Variogram({})
    this.trend = trend || new Trend({})
    this.settings = settings || defaultSettings(this.parent)
    if (crossSection) {
      this.settings.crossSection = crossSection
    }
    // TODO: Make sure the class knows that the data is actually from the CURRENT specification
    //   E.g. use a hash of the specification (variogram, trend, and settings)
    this.waiting = false
    this._data = []
  }

  public get simulated (): boolean {
    return this._data.length > 0 && this._data[0].length > 0
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
}

type GaussianRandomFields = Identified<GaussianRandomField>

export {
  Variogram,
  Trend,
  GaussianRandomField,
  GaussianRandomFields,
}

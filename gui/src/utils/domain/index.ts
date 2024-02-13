import { Facies, GlobalFacies, FaciesGroup } from '@/utils/domain/facies'
import GaussianRandomField from '@/utils/domain/gaussianRandomField'
import Region from '@/utils/domain/region'
import {
  Bayfill,
  NonCubic,
  Cubic,
  Direction,
} from '@/utils/domain/truncationRule/index'
import Zone from '@/utils/domain/zone'
import Polygon from '@/utils/domain/polygon/base'
import BayfillPolygon from '@/utils/domain/polygon/bayfill'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import CubicPolygon from '@/utils/domain/polygon/cubic'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import type { ParentReference } from '@/utils/domain/bases/interfaces'
import type {
  Parent,
  Dependent,
} from '@/utils/domain/bases/zoneRegionDependent'

export type InstantiatedOverlayTruncationRule = NonCubic | Cubic
type InstantiatedTruncationRule = Bayfill | InstantiatedOverlayTruncationRule

export {
  Direction,
  type Dependent,
  type Parent,
  type ParentReference,
  Polygon,
  BayfillPolygon,
  CubicPolygon,
  NonCubicPolygon,
  OverlayPolygon,
  Region,
  Zone,
  GlobalFacies,
  Facies,
  FaciesGroup,
  GaussianRandomField,
  type InstantiatedTruncationRule,
  Bayfill,
  NonCubic,
  Cubic,
}

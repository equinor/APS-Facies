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
import { ParentReference } from '@/utils/domain/bases/interfaces'
import { Parent, Dependent } from '@/utils/domain/bases/zoneRegionDependent'

type TruncationRule = Bayfill | NonCubic | Cubic

export {
  Direction,
  Dependent,
  Parent,
  ParentReference,
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
  TruncationRule,
  Bayfill,
  NonCubic,
  Cubic,
}
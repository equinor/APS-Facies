import { Facies, GlobalFacies } from '@/utils/domain/facies'
import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import Region from '@/utils/domain/region'
import {
  Bayfill,
  NonCubic,
  Cubic,
} from '@/utils/domain/truncationRule/index'
import Zone from '@/utils/domain/zone'
import Polygon from '@/utils/domain/polygon/base'
import BayfillPolygon from '@/utils/domain/polygon/bayfill'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import CubicPolygon from '@/utils/domain/polygon/cubic'
import OverlayPolygon from '@/utils/domain/polygon/overlay'

type TruncationRule = Bayfill | NonCubic | Cubic

export {
  Polygon,
  BayfillPolygon,
  CubicPolygon,
  NonCubicPolygon,
  OverlayPolygon,
  Region,
  Zone,
  GlobalFacies,
  Facies,
  GaussianRandomField,
  TruncationRule,
  Bayfill,
  NonCubic,
  Cubic,
}

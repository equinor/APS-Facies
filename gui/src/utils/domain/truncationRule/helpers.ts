import type TruncationRule from '@/utils/domain/truncationRule/base'
import type Polygon from '@/utils/domain/polygon/base'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type OverlayPolygon from '@/utils/domain/polygon/overlay'
import type {
  OverlayPolygonSerialization,
  OverlayPolygonSpecification,
} from '@/utils/domain/polygon/overlay'
import { Bayfill } from '@/utils/domain'
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

export function isOverlayTruncationRule<
  T extends Polygon | OverlayPolygon,
  S extends PolygonSerialization | OverlayPolygonSerialization,
  P extends PolygonSpecification | OverlayPolygonSpecification,
  R extends TruncationRule<T, S, P>,
  O extends OverlayTruncationRule<T, S, P>,
>(rule: R | O): rule is O {
  if (rule instanceof Bayfill) {
    return false
  }
  return 'isUsedInOverlay' in rule
}

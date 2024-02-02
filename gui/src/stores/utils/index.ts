import { getId } from '@/utils'
import type { Parent, ParentReference } from '@/utils/domain'
import { useZoneStore } from '@/stores/zones'

export function resolveParentReference(parentRef: ParentReference | Parent): Parent {
  const zoneStore = useZoneStore()
  const zone = zoneStore.identifiedAvailable[getId(parentRef.zone)]
  if (!zone)
    throw new Error(`The zone with reference '${parentRef.zone}' is missing`)
  const region =
    zone.regions.find((r) => r.id === getId(parentRef.region)) ?? null
  return {
    zone,
    region,
  }
}

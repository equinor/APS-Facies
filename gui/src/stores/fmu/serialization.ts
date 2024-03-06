import type { FmuMaxDepthStoreSerialization } from '@/stores/fmu/maxDepth'
import { useFmuMaxDepthStoreSerialization } from '@/stores/fmu/maxDepth'
import type { FmuOptionsSerialization } from '@/stores/fmu/options'
import { useFmuOptionsSerialization } from '@/stores/fmu/options'

export interface FmuStoreSerialization extends FmuOptionsSerialization{
    maxDepth: FmuMaxDepthStoreSerialization
}

export function useFmuStoreSerialization (): FmuStoreSerialization {
    return {
        maxDepth: useFmuMaxDepthStoreSerialization(),
        ...useFmuOptionsSerialization(),
    }
}

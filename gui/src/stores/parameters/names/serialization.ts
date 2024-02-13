import type { SelectableSerialization } from '@/stores/parameters/serialization/helpers'
import { useParameterNameModelStore } from '@/stores/parameters/names/model'
import { useParameterNameProjectStore } from '@/stores/parameters/names/project'
import { useParameterNameWorkflowStore } from '@/stores/parameters/names/workflow'

export type ParameterNameStoreSerialization = {
    model: SelectableSerialization
    project: SelectableSerialization
    workflow: SelectableSerialization
}

export function useParameterNameStoreSerialization():ParameterNameStoreSerialization {
    return {
        model: { selected: useParameterNameModelStore().selected },
        project: { selected: useParameterNameProjectStore().selected },
        workflow: { selected: useParameterNameWorkflowStore().selected },
    }
}

# -*- coding: utf-8 -*-
def running_in_batch_mode():
    try:
        import roxar.rms
    except ImportError:
        return False
    return roxar.rms.get_execution_mode() == roxar.ExecutionMode.Batch

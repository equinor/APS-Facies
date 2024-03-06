interface Selector {
  onSelectionChanged(func: (changed: Rectord<string, any>) => void)
  setSelection(selection)
  getSelection(): Record<string, any>
}

interface SerializedState {
  [_: string]: any
}

interface RmsJob extends SerializedState {
  _treeorigin: string
  _version: string
}

declare namespace rms {
  declare namespace uipy {
    function call<T>(name: string, ...args: any[]): Promise<T>
  }
  function onPluginSave(func: () => SerializedState): void
  function onPluginLoaded(func: (data: RmsJob) => void): void
  function onProjectChanged(func: (what: any) => void): void
  function onRunExecuted(func: () => void): void
  function onRunCompleted(func: (output: string, reason: string) => void): void
  function chooseFile(mode: 'save' | 'load', filter = '', suggestion = ''): Promise<string>
  function chooseDir(mode: 'save' | 'load', suggestion: string = ''): Promise<string | null>
  function createSelector(
    id: string,
    collections: ('horizons' | 'wells' | 'trajectories' | 'points' | 'polylines' | 'surfaces' | 'properties' | 'grids' | 'blocked_wells')[],
    single: boolean,
    selector?: Record<string, string>,
  ): Selector
}

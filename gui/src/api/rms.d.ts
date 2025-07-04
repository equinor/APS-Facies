interface Selector {
  onSelectionChanged(func: (changed: Rectord<string, unknown>) => void)
  setSelection(selection)
  getSelection(): Record<string, unknown>
}

interface SerializedState {
  [_: string]: unknown
}

interface RmsJob extends SerializedState {
  _treeorigin: string
  _version: string
}

declare namespace rms {
  declare namespace uipy {
    function call<T>(name: string, ...args: unknown[]): Promise<T>
  }
  function onPluginSave(func: () => Job): void
  function onPluginLoaded(func: (data: RmsJob) => void): void
  function onProjectChanged(func: (what: unknown) => void): void
  function onRunExecuted(func: () => void): void
  function onRunCompleted(func: (output: string, reason: string) => void): void
  function chooseFile(
    mode: 'save' | 'load',
    filter = '',
    suggestion = '',
  ): Promise<string>
  function chooseDir(
    mode: 'save' | 'load',
    suggestion: string = '',
  ): Promise<string | null>
  function createSelector(
    id: string,
    collections: (
      | 'horizons'
      | 'wells'
      | 'trajectories'
      | 'points'
      | 'polylines'
      | 'surfaces'
      | 'properties'
      | 'grids'
      | 'blocked_wells'
    )[],
    single: boolean,
    selector?: Record<string, string>,
  ): Selector
}

/**
 * Mock of the demo project 'Emerald_10_1.pro'
 */
// eslint-disable-next-line no-undef
const api = typeof rms !== 'undefined' ? rms.uipy : {
  // This is a mock of ui.py
  get_grid_names: () => new Promise((resolve, reject) => {
    resolve([
      {id: 1, name: 'Deterministic'},
      {id: 2, name: 'Heterogeneity'},
      {id: 3, name: 'PropTrends'},
      {id: 4, name: 'UpscaledModel'},
      {id: 5, name: 'AI'},
      {id: 6, name: 'Tempest Import'},
      {id: 7, name: 'GeoModel'},
      {id: 8, name: 'FlowModel'},
      {id: 9, name: 'StructModGrid'},
      {id: 10, name: 'MultiPointGrid'},
      {id: 11, name: 'EditModel'},
      {id: 12, name: 'RoxarAPI'},
    ])
  })
}

const gridModels = api.get_grid_names()

const zones = [
  {id: 1, name: 'ZoneC', regions: [{id: 1, name: 'Region 1'}, {id: 2, name: 'Region 2'}]},
  {id: 2, name: 'TopC_BaseA', regions: []},
  {id: 3, name: 'ZoneB', regions: []},
  {
    id: 4,
    name: 'ZoneA',
    regions: [
      {id: 1, name: 'Region 1'},
      {id: 2, name: 'Region 2'},
      {id: 3, name: 'Region 3'},
      {id: 4, name: 'Region 4'},
      {id: 5, name: 'Region 5'},
    ]},
]

const facies = [
  {code: 1, name: 'F1', color: '#7cfc00'},
  {code: 2, name: 'F2', color: '#808080'},
  {code: 3, name: 'F3', color: '#1e90ff'},
  {code: 4, name: 'F4', color: '#ffd700'},
  {code: 5, name: 'F5', color: '#9932cc'},
  {code: 6, name: 'F6', color: '#00ffff'},
  {code: 7, name: 'F7', color: '#b22222'},
  {code: 8, name: 'F8', color: '#6b8e23'},
  {code: 9, name: 'F9', color: '#0000ff'},
  {code: 10, name: 'F10', color: '#dc143c'},
  {code: 11, name: 'F11', color: '#ff8c00'},
  {code: 12, name: 'F12', color: '#ff0000'},
]

export default {
  gridModels,
  zones,
  facies,
}

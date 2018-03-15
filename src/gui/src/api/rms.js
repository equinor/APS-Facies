/**
 * Mock of the demo project 'Emerald_10_1.pro'
 */

const randomHexColor = require('random-hex-color')

const gridModels = [
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
]

const zones = [
  {id: 1, name: 'ZoneC', regions: [{name: 'Region 1'}, {name: 'Region 2'}, {name: 'Region 3'}, {name: 'Region 4'}]},
  {id: 2, name: 'TopC_BaseA', regions: [{name: 'A Region'}, {name: 'Another Region'}, {name: 'A third region'}]},
  {id: 3, name: 'ZoneB'},
  {id: 4, name: 'ZoneA', regions: []},
]

const facies = [
  {code: 1, name: 'F1', color: randomHexColor()},
  {code: 2, name: 'F2', color: randomHexColor()},
  {code: 3, name: 'F3', color: randomHexColor()},
  {code: 4, name: 'F4', color: randomHexColor()},
  {code: 5, name: 'F5', color: randomHexColor()},
  {code: 6, name: 'F6', color: randomHexColor()},
  {code: 7, name: 'F7', color: randomHexColor()},
  {code: 8, name: 'F8', color: randomHexColor()},
  {code: 9, name: 'F9', color: randomHexColor()},
  {code: 10, name: 'F10', color: randomHexColor()},
]

export default {
  gridModels,
  zones,
  facies,
}

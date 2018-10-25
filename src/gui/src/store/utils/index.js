const promiseSimpleCommit = (commit, commitment, data, check = true, error = '') => {
  return new Promise((resolve, reject) => {
    if (check) {
      commit(commitment, data)
      resolve(data)
    } else {
      reject(error)
    }
  })
}

const compareFacies = (facies, other, beStrict = false) => {
  let equal = facies.name === other.name && facies.code === other.code
  if (beStrict) {
    equal = equal && facies.color === other.color
  }
  return equal
}

const indexOfFacies = (state, facies) => { return state.available.findIndex(item => compareFacies(item, facies)) }

const fetchParameterHelper = (commit, dispatch, promise) => {
  return promise
    .then(result => {
      commit('AVAILABLE', result)
      if (result.length === 1) {
        dispatch('select', result[0])
      } else if (result.length === 0) {
        dispatch('select', null)
      }
    })
}

const mirrorZoneRegions = store => {
  store.subscribe(({ type, payload }, state) => {
    if (
      type.startsWith('zones') &&
      state.regions.use &&
      !!state.zones.current
    ) {
      if (type === 'zones/REGIONS') {
        store.commit('regions/AVAILABLE', { regions: payload.regions })
      } else if (type === 'zones/CURRENT') {
        store.commit('regions/AVAILABLE', { regions: state.zones.available[`${payload.id}`].regions })
      } else if (type === 'zones/SELECTED') {
        // Nothing to do.
        // Handled by zone's selected action
      } else if (type === 'zones/REGION_SELECTED') {
        // Nothing to do.
        // Handled by regions's selected action
      } else {
        throw new Error(`Unsupported commit type, ${type}`)
      }
    }
  })
}

export {
  promiseSimpleCommit,
  indexOfFacies,
  fetchParameterHelper,
  mirrorZoneRegions,
  compareFacies
}

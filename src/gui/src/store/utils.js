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

export {
  promiseSimpleCommit,
  indexOfFacies,
  fetchParameterHelper,
  compareFacies
}

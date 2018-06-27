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

const indexOfFacies = (state, facies) => { return state.availableFacies.findIndex(item => compareFacies(item, facies)) }

export {
  promiseSimpleCommit,
  indexOfFacies,
  compareFacies
}

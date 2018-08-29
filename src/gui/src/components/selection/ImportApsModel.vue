<template>
  <label
    class="file-select"
  >
    <div
      class="v-btn theme--dark primary"
    >
      <span>Open</span>
    </div>
    <input
      type="file"
      @change="handleFileChange"
    >
  </label>
</template>

<script>

import rms from '@/api/rms'

const tryParse = xmlString => {
  const parser = new DOMParser()
  const parsererrorNS = parser.parseFromString('INVALID', 'text/xml').getElementsByTagName('parsererror')[0].namespaceURI
  const dom = parser.parseFromString(xmlString, 'text/xml')
  if (dom.getElementsByTagNameNS(parsererrorNS, 'parsererror').length > 0) {
    throw new Error('Error parsing XML')
  }
  return dom
}

const loadFile = dom => {
  alert('Your file was instantiated OK as an APS Model, but population of the User interface is not implemented')
}

export default {

  methods: {
    handleFileChange (e) {
      const selectedFile = e.target.files[0]
      if (selectedFile.type === 'text/xml') {
        const reader = new FileReader()
        reader.onload = function (e) {
          const fileContent = reader.result
          console.log('file read ok')
          try {
            const dom = tryParse(fileContent)
            console.log('file parsed ok')
            rms.isApsModelValid(btoa(new XMLSerializer().serializeToString(dom)))
              .then(result => {
                console.log(result)
                if (result.valid) {
                  loadFile(dom)
                } else {
                  alert('something failed')
                  alert(result)
                }
              }
              )
          } catch (Err) {
            alert('The file you tried to open is not valid XML and cannot be used')
          }
        }
        reader.readAsText(selectedFile)
      } else {
        alert('The file you tried to open is not an xml file and cannot be used')
      }
      this.$emit('input', e.target.files[0])
    }
  }
}
</script>

<style scoped>

.file-select > input[type="file"] {
  display: none;
}

</style>

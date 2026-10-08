// Chromium 69 (RMS 14.2) has no flexbox 'gap', so Vuetify's 'ga-*' does nothing.
// Marks the page, so that 'style/main.scss' can fall back to margins
export function markMissingFlexGap(): void {
  const flex = document.createElement('div')
  flex.style.display = 'flex'
  flex.style.flexDirection = 'column'
  flex.style.rowGap = '1px'
  flex.append(document.createElement('div'), document.createElement('div'))
  document.body.append(flex)
  const hasFlexGap = flex.scrollHeight === 1
  flex.remove()
  document.documentElement.classList.toggle('no-flex-gap', !hasFlexGap)
}

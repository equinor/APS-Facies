import MarkdownIt from 'markdown-it'
// @ts-ignore
import MarkdownItFootnote from 'markdown-it-footnote'

const md = MarkdownIt()
  .use(MarkdownItFootnote)

export default md

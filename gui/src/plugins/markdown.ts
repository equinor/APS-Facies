import MarkdownIt from 'markdown-it'
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import MarkdownItFootnote from 'markdown-it-footnote'

const md = MarkdownIt().use(MarkdownItFootnote)

export default md

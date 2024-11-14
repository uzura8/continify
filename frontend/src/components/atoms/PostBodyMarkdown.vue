<template>
  <div
    v-html="bodyMarkdown"
    class="post-body"
  ></div>
</template>
<script>
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark-dimmed.css'

let isMarkedApplied = false

export default {
  props: {
    body: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      bodyMarkdown: '',
    }
  },

  created() {
    if (!isMarkedApplied) {
      marked.setOptions({ breaks: true })
      marked.use(
        markedHighlight({
          langPrefix: 'hljs language-',
          highlight(code, lang) {
            const language = hljs.getLanguage(lang) ? lang : 'plaintext'
            return hljs.highlight(code, { language }).value
          }
        })
      )
      isMarkedApplied = true
    }
    this.bodyMarkdown = marked(this.body)
  },
}
</script>
<style lang="scss">
.post-body {
  pre {
    padding: 0.5rem;
    font-size: 1.1rem;
  }
}
</style>

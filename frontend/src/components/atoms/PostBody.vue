<template>
  <div
    v-html="body"
    class="post-body"
  ></div>
</template>
<script>
//import marked from 'marked'
//import hljs from 'highlight.js'
import { siteMixin } from '@/mixins/site'

export default {
  mixins: [siteMixin],

  components: {},

  props: {
    body: {
      type: String,
      default: ''
    }
    //bodyFormat: {
    //  type: String,
    //  default: 'html',
    //}
  },

  data() {
    return {}
  },

  computed: {},

  created() {
    //marked.setOptions({
    //  highlight: function (code, lang) {
    //    if (lang && hljs.getLanguage(lang)) {
    //      return hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
    //    } else {
    //      return hljs.highlightAuto(code).value
    //    }
    //  }
    //})
  },

  mounted() {
    //this.bodyMarkdown = marked.parse(this.body)
  },

  mounted() {
    //window.hljs.highlightAll()
  },

  methods: {}
}
</script>
<style lang="scss">
.post-body {
  pre {
    padding: 0 0;
  }
}
</style>

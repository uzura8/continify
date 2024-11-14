<template>
  <div class="post-body-json">
    <pre><code class="highlight-json">{{ formattedBodyJson }}</code></pre>
  </div>
</template>
<script>
import 'highlight.js/styles/atom-one-dark.css'
import hljs from 'highlight.js'
window.hljs = hljs

export default {
  name: 'PostBody',

  components: {},

  props: {
    bodyJson: {
      type: Object,
      default: null
    }
  },

  data() {
    return {}
  },

  computed: {
    formattedBodyJson() {
      return JSON.stringify(this.bodyJson, null, '  ').trim()
    }
  },

  mounted() {
    window.hljs.highlightAll()
  },

  methods: {}
}
</script>
<style lang="scss">
.post-body-json {
  pre {
    padding: 0.5rem;
  }
}
</style>


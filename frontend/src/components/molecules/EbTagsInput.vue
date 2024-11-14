<template>
  <input
    id="tagsInput"
    ref="tagsInput"
    class="input"
    type="text"
    name="tags"
    :value="value"
    autocomplete
    @change="updated"
  />
</template>
<script>
import Tagify from '@yaireo/tagify'
import '@yaireo/tagify/dist/tagify.css'

export default {
  props: {
    tags: {
      type: Array,
      default: () => []
    },
    existedTags: {
      type: Array,
      default: () => []
    }
  },

  emits: ['updated'],

  data() {
    return {
      tagify: null,
      value: ''
    }
  },

  computed: {
    whitelist() {
      let whitelist = []
      this.existedTags.map((item) => {
        whitelist.push(item.label)
      })
      return whitelist
    }
  },

  watch: {
    tags(val) {
      this.value = JSON.stringify(val)
    },

    whitelist(val) {
      this.tagify.whitelist = val
    }
  },

  created() {
    this.value = JSON.stringify(this.tags)
  },

  mounted() {
    this.$nextTick(() => {
      console.log('mounted', this.whitelist)
      const tagsInput = this.$refs.tagsInput
      if (tagsInput) {
        this.tagify = new Tagify(tagsInput, {
          whitelist: this.whitelist,
          dropdown: {
            classname: 'color-blue',
            enabled: 1,
            maxItems: 10,
            position: 'text',
            closeOnSelect: false,
            highlightFirst: true
          }
        })
      } else {
        console.error('tagsInput not found')
      }
    })
  },

  methods: {
    updated(e) {
      let vals
      if (typeof e.target.value === 'string' && e.target.value.trim() !== '') {
        try {
          vals = JSON.parse(e.target.value)
        } catch (error) {
          console.error('Failed to parse JSON:', error)
          vals = e.target.value // JSONパースが失敗した場合のフォールバック
        }
      } else {
        vals = []
      }
      this.$emit('updated', vals)
    }
  }
}
</script>

<template>
  <div>
    <editor
      :value="value"
      :api-key="tinyMCEApiKey"
      :init="editorOptions"
      :initial-value="value"
      @change="changeValue"
    ></editor>
  </div>
</template>
<script>
import config from '@/config/config'
import Editor from '@tinymce/tinymce-vue'

export default {
  name: 'RichTextEditor',

  components: {
    editor: Editor
  },

  props: {
    value: {
      type: String,
      default: ''
    },

    editorMergeOptions: {
      type: Object,
      default: () => {
        return {}
      }
    }
  },

  data() {
    return {
      editorDefaultOptions: {
        height: 500,
        language: 'ja',
        forced_root_block: 'p',
        // paste_as_text: true, // デフォルトでテキストとして貼り付ける
        plugins: [
          'emoticons',
          'hr',
          'code',
          'lists',
          'link',
          'image',
          'preview',
          'anchor',
          'visualblocks',
          'table',
          'help',
          'fullscreen',
          'paste',
          'advlist',
          'autolink',
          'autosave'
        ],
        menubar: true, // menubar: true でデフォルトのメニューバーを有効にする
        toolbar: [
          { name: 'history', items: ['undo', 'redo'] },
          {
            name: 'formatting',
            items: ['bold', 'italic', 'backcolor', 'forecolor', 'removeformat']
          },
          { name: 'alignment', items: ['alignleft', 'aligncenter', 'alignright', 'alignjustify'] },
          { name: 'lists', items: ['bullist', 'numlist'] },
          { name: 'indentation', items: ['outdent', 'indent'] },
          { name: 'insert', items: ['hr', 'table', 'link', 'anchor', 'emoticons'] },
          { name: 'tools', items: ['visualblocks', 'code', 'fullscreen', 'preview', 'help'] }
        ]
      }
    }
  },

  computed: {
    tinyMCEApiKey() {
      return config.tinyMCEApiKey
    },

    editorOptions() {
      return Object.assign({}, this.editorDefaultOptions, this.editorMergeOptions)
    }
  },

  methods: {
    changeValue(e) {
      // this.$emit('input', event)
      this.$emit('input', e.target.getContent())
    }
  }
}
</script>

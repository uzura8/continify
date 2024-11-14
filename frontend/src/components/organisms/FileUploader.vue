<script>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ulid } from 'ulid'
import FileUpload from 'primevue/fileupload'
import FileUploaderImage from '@/components/organisms/FileUploaderImage'
import FileUploaderFile from '@/components/organisms/FileUploaderFile'

export default {
  components: {
    FileUpload,
    FileUploaderImage,
    FileUploaderFile
  },

  props: {
    fileType: {
      type: String,
      required: true,
      default: 'image'
    },

    modelValue: {
      type: Array,
      required: false,
      default: () => []
    },

    imageActionButtonType: {
      type: String,
      required: false,
      default: 'insert'
    },

    fileActionButtonType: {
      type: String,
      required: false,
      default: 'copy'
    },

    uploaderOptions: {
      type: Object,
      required: true,
      default: null
    }
  },

  emits: ['insertImage', 'copyUrl'],

  setup(props, context) {
    const { t } = useI18n()

    const files = ref([])
    props.modelValue.forEach((file) => {
      files.value.push(file)
    })

    const handleUpload = (event) => {
      for (let fileObj of event.target.files) {
        fileObj.fileId = ulid().toLowerCase()
        files.value.push(fileObj)
      }
    }

    const buttonLabel = computed(() => {
      const labelKey = props.fileType === 'image' ? 'form.SelectImages' : 'form.SelectFiles'
      return t(labelKey)
    })

    const getUploadConfig = (key, defaultVal) => {
      if (key in props.uploaderOptions) {
        return props.uploaderOptions[key]
      }
      return defaultVal
    }

    const setUploadedFile = (payload) => {
      const index = files.value.findIndex((item) => {
        return item.fileId === payload.fileId
      })
      if (index === -1) return

      files.value.splice(index, 1, payload)
      context.emit('update:modelValue', files.value)
    }

    const inputCaption = (payload) => {
      const index = files.value.findIndex((item) => {
        return item.fileId === payload.fileId
      })
      if (index === -1) return

      let sevedFile = { ...files.value[index] }
      sevedFile.caption = payload.caption
      files.value.splice(index, 1, sevedFile)
      context.emit('update:modelValue', files.value)
    }

    const deleteFile = (fileId) => {
      const index = files.value.findIndex((item) => item.fileId === fileId)
      files.value.splice(index, 1)
      context.emit('update:modelValue', files.value)
    }

    const insertImage = (payload) => {
      context.emit('insert-image', payload)
    }

    const copyUrl = (payload) => {
      context.emit('copy-url', payload)
    }

    return {
      files,
      handleUpload,
      setUploadedFile,
      buttonLabel,
      getUploadConfig,
      inputCaption,
      deleteFile,
      insertImage,
      copyUrl
    }
  }
}
</script>

<template>
  <ul class="columns is-multiline">
    <li
      v-for="file in files"
      class="column"
      :class="{
        'is-half-tablet is-one-third-desktop is-one-quarter-widescreen': fileType === 'image',
        'is-multiline': fileType === 'file'
      }"
    >
      <FileUploaderImage
        v-if="fileType === 'image'"
        :file="file"
        :enableCaption="true"
        :actionButtonType="imageActionButtonType"
        :uploaderOptions="uploaderOptions"
        @uploaded="setUploadedFile"
        @delete-file="deleteFile"
        @input-caption="inputCaption"
        @insert-image="insertImage"
      />
      <FileUploaderFile
        v-else
        :file="file"
        :enableCaption="true"
        :action-button-type="fileActionButtonType"
        :uploaderOptions="uploaderOptions"
        @uploaded="setUploadedFile"
        @delete-file="deleteFile"
        @input-caption="inputCaption"
        @copy-url="copyUrl"
        :uploader-options="uploaderOptions"
        class="file-label"
      />
    </li>
  </ul>
  <div>
    <div class="file">
      <label class="file-label">
        <input
          class="file-input"
          type="file"
          multiple
          :accept="getUploadConfig('mimeTypes', []).join(',')"
          @change="handleUpload"
        />
        <span class="file-cta">
          <span class="file-icon">
            <i class="fas fa-upload"></i>
          </span>
          <span class="file-label">{{ buttonLabel }}</span>
        </span>
      </label>
    </div>
  </div>
</template>

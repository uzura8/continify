<script>
import axios from 'axios'
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import utilObj from '@/util/obj'
import { Admin } from '@/api'
import utilStr from '@/util/str'
import utilSite from '@/util/site'
import InputText from 'primevue/inputtext'
import BLoading from '@/components/molecules/BLoading'
import BSelect from '@/components/atoms/BSelect'
import FbImg from '@/components/atoms/FbImg'

export default {
  components: {
    InputText,
    BLoading,
    BSelect,
    FbImg
  },

  props: {
    file: {
      type: Object,
      required: true,
      default: null
    },

    enableCaption: {
      type: Boolean,
      default: false
    },

    actionButtonType: {
      type: String,
      required: false,
      default: 'insert'
    },

    uploaderOptions: {
      type: Object,
      required: true,
      default: null
    }
  },

  setup(props, context) {
    const store = useStore()
    const { t } = useI18n()
    const route = useRoute()

    const serviceId = computed(() => {
      return route.params.serviceId
    })

    const isUploading = ref(false)
    const error = ref('')

    const isFileObject = computed(() => {
      return props.file instanceof File
    })

    const isUploaded = computed(() => {
      return isFileObject.value === false
    })

    const getUploadConfig = (key, defaultVal) => {
      if (key === 'size') {
        return Number(props.uploaderOptions.sizeLimitMB) * 1024 * 1024
      }
      if (key in props.uploaderOptions) {
        return props.uploaderOptions[key]
      }
      return defaultVal
    }

    const blobSrc = computed(() => {
      if (isFileObject.value === false) return null
      return URL.createObjectURL(props.file)
    })

    const validate = () => {
      if (utilStr.checkExtension(props.file.name, getUploadConfig('extensions')) === false) {
        error.value = t('msg.invalidError', { field: t('common.extention') })
        return
      }

      const mimeTypes = getUploadConfig('mimeTypes', [])
      if (mimeTypes && mimeTypes.includes(props.file.type) === false) {
        error.value = t('msg.invalidError', { field: t('common.fileType') })
        return
      }

      const sizeLimit = getUploadConfig('size', 0)
      if (sizeLimit && props.file.size > sizeLimit) {
        error.value = t('msg.overMaxSizeOnUpload', { max: utilStr.bytesFormat(sizeLimit) })
        return
      }
    }

    const uploadToS3 = async (url) => {
      try {
        isUploading.value = true
        const res = await axios({
          method: 'PUT',
          url: url,
          headers: { 'Content-Type': props.file.type },
          data: props.file
        })
        isUploading.value = false
        return res
      } catch (err) {
        utilSite.debugOutput(err)
        isUploading.value = false
        error.value = t('msg["Upload failed"]')
      }
    }

    const createS3PreSignedUrl = async () => {
      try {
        let vals = {
          fileId: props.file.fileId,
          fileType: 'image',
          mimeType: props.file.type,
          name: props.file.name,
          size: props.file.size
        }
        isUploading.value = true
        const res = await Admin.createS3PreSignedUrl(
          serviceId.value,
          vals,
          store.state.adminUser.token
        )
        isUploading.value = false
        return res
      } catch (err) {
        utilSite.debugOutput(err)
        isUploading.value = false
        error.value = t('msg["Upload failed"]')
      }
    }

    const upload = async () => {
      validate()
      if (error.value) return

      const reserved = await createS3PreSignedUrl()
      if (!reserved) return

      const emitData = { fileId: reserved.fileId, mimeType: reserved.mimeType }

      const res = await uploadToS3(reserved.url)
      if (!res) return

      context.emit('uploaded', emitData)
    }

    const deleteFile = async () => {
      if (isFileObject.value) {
        context.emit('delete-file', props.file.fileId)
        return
      }
      try {
        isUploading.value = true
        await Admin.deleteFile(serviceId.value, props.file.fileId, store.state.adminUser.token)
        isUploading.value = false
        context.emit('delete-file', props.file.fileId)
      } catch (err) {
        utilSite.debugOutput(err)
        error.value = t('msg["Delete failed"]')
        isUploading.value = false
      }
    }

    const caption = ref('')
    const inputCaption = () => {
      const emitData = { fileId: props.file.fileId, caption: caption }
      context.emit('input-caption', emitData)
    }

    const sizes = computed(() => {
      if (utilObj.isEmpty(props.uploaderOptions)) return []
      return props.uploaderOptions.sizes
    })

    const insertSize = ref('raw')
    const insertImage = () => {
      const imgUrl = utilSite.mediaUrl(
        serviceId.value,
        'image',
        props.file.fileId,
        props.file.mimeType,
        insertSize.value
      )
      context.emit('insert-image', { url: imgUrl, caption: caption.value })
    }

    onMounted(async () => {
      if (props.file.caption) caption.value = props.file.caption
      if (!isUploaded.value) {
        await upload()
      }
    })

    return {
      blobSrc,
      insertSize,
      deleteFile,
      insertImage,
      caption,
      isUploaded,
      isUploading,
      inputCaption,
      sizes,
      error
    }
  }
}
</script>

<template>
  <div class="upload-image-box">
    <div
      v-if="isUploaded === false"
      class="image"
    >
      <img :src="blobSrc" />
    </div>
    <div
      v-else
      class="image"
    >
      <FbImg
        :fileId="file.fileId"
        :mimeType="file.mimeType"
        size="raw"
      />
    </div>

    <div class="mt-3">
      <div
        v-if="error"
        class="has-text-danger"
      >
        {{ error }}
      </div>
      <div
        v-else-if="isUploaded"
        class="has-text-success"
      >
        Uploaded
      </div>
    </div>

    <div
      v-if="enableCaption && isUploaded"
      class="mt-4"
    >
      <div class="field">
        <span class="p-float-label">
          <InputText
            id="value"
            v-model="caption"
            @blur="inputCaption"
            class="w-full"
          />
          <label for="value">{{ $t('common.caption') }}</label>
        </span>
      </div>
    </div>

    <div
      v-if="isUploaded"
      class="mt-3"
    >
      <BSelect v-model="insertSize">
        <option value="raw">{{ $t('common.originalSize') }}</option>
        <option
          v-for="size in sizes"
          :value="size"
        >
          {{ size }}
        </option>
      </BSelect>
      <div class="mt-2">
        <button
          class="button"
          @click="insertImage"
        >
          <span class="icon">
            <i
              v-if="actionButtonType === 'copy'"
              class="fas fa-copy"
            ></i>
            <i
              v-else
              class="fas fa-plus"
            ></i>
          </span>
          <span v-if="actionButtonType === 'copy'">{{ $t('common.copy') }}</span>
          <span v-else>{{ $t('common.insertOf', { name: $t('common.image') }) }}</span>
        </button>
      </div>
      <div
        v-if="isUploaded"
        class="mt-2 has-text-warning-dark"
      >
        {{ $t('msg.generateItemRequiresTimes', { target: $t('common.thumbnails') }) }}
      </div>
    </div>

    <button
      class="button is-light is-small btn-delete"
      @click="deleteFile"
    >
      <span class="icon">
        <i class="fas fa-times-circle"></i>
      </span>
    </button>
    <BLoading
      :is-full-page="false"
      :active="isUploading"
    />
  </div>
</template>

<style scoped>
.upload-image-box {
  position: relative;
}
.btn-delete {
  position: absolute;
  top: 10px;
  right: 10px;
}
</style>

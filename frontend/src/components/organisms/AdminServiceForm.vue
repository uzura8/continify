<template>
  <div>
    <div class="field">
      <label class="font-semibold mt-5">serviceId</label>
      <p
        v-if="isEdit"
        class="p-2"
      >
        {{ service.serviceId }}
      </p>
      <InputText
        v-else
        v-model="serviceIdInput"
        type="text"
        class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
        :class="{ 'p-invalid': checkEmpty(errors.serviceIdInput) === false }"
        @blur="validate('serviceIdInput')"
      />
      <p
        v-if="checkEmpty(errors.serviceIdInput) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.serviceIdInput[0] }}
      </p>
    </div>

    <div class="field mt-3">
      <label class="font-semibold">label</label>
      <InputText
        v-model="label"
        class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
        :class="{ 'p-invalid': checkEmpty(errors.label) === false }"
        @blur="validate('label')"
      />
      <p
        v-if="checkEmpty(errors.label) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.label[0] }}
      </p>
    </div>

    <div class="field mb-2">
      <label class="font-semibold mt-5">{{ $t('form.functionToApply') }}</label>
      <div class="flex align-items-center">
        <label class="checkbox">
          <input
            v-model="functions"
            value="post"
            type="checkbox"
          />
          {{ $t('term.availableFunctions.post') }}
        </label>
      </div>
    </div>

    <div
      v-if="functions.includes('post')"
      class="pl-5 pt-2 pb-4"
    >
      <div class="field">
        <label class="font-semibold">{{ $t('form.outerSiteUrl') }}</label>
        <InputText
          v-model="outerSiteUrl"
          class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
          :class="{ 'p-invalid': checkEmpty(errors.label) === false }"
          @blur="validate('outerSiteUrl')"
        />
        <p
          v-if="checkEmpty(errors.outerSiteUrl) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.outerSiteUrl[0] }}
        </p>
      </div>

      <div class="field mt-5">
        <label class="font-semibold">{{ $t('form.frontendPostDetailUrlPrefix') }}</label>
        <InputText
          v-model="frontendPostDetailUrlPrefix"
          class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
          :class="{ 'p-invalid': checkEmpty(errors.frontendPostDetailUrlPrefix) === false }"
          @blur="validate('frontendPostDetailUrlPrefix')"
        />
        <p
          v-if="checkEmpty(errors.frontendPostDetailUrlPrefix) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.frontendPostDetailUrlPrefix[0] }}
        </p>
      </div>

      <div class="field mt-5">
        <label class="font-semibold">
          {{ $t('form.mediaUploadAcceptMimetypesFor', { target: $t('common.images') }) }}
        </label>
        <InputText
          v-model="mediaUploadAcceptMimetypesImage"
          class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
          :class="{ 'p-invalid': checkEmpty(errors.mediaUploadAcceptMimetypesImage) === false }"
          @blur="validate('mediaUploadAcceptMimetypesImage')"
        />
        <p
          v-if="checkEmpty(errors.mediaUploadAcceptMimetypesImage) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.mediaUploadAcceptMimetypesImage[0] }}
        </p>
      </div>

      <div class="field mt-5">
        <label class="font-semibold">
          {{ $t('form.mediaUploadImageSizes') }}
        </label>
        <InputText
          v-model="mediaUploadImageSizes"
          class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
          :class="{ 'p-invalid': checkEmpty(errors.mediaUploadImageSizes) === false }"
          @blur="validate('mediaUploadImageSizes')"
        />
        <p
          v-if="checkEmpty(errors.mediaUploadImageSizes) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.mediaUploadImageSizes[0] }}
        </p>
      </div>

      <div class="field mt-5">
        <label class="font-semibold">
          {{ $t('form.mediaUploadSizeLimitMBImage') }}
        </label>
        <InputText
          v-model="mediaUploadSizeLimitMBImage"
          class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
          :class="{ 'p-invalid': checkEmpty(errors.mediaUploadSizeLimitMBImage) === false }"
          @blur="validate('mediaUploadSizeLimitMBImage')"
        />
        <p
          v-if="checkEmpty(errors.mediaUploadSizeLimitMBImage) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.mediaUploadSizeLimitMBImage[0] }}
        </p>
      </div>

      <div class="field mt-5">
        <label class="font-semibold">
          {{ $t('form.mediaUploadAcceptMimetypesFor', { target: $t('common.files') }) }}
        </label>
        <InputText
          v-model="mediaUploadAcceptMimetypesFile"
          class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
          :class="{ 'p-invalid': checkEmpty(errors.mediaUploadAcceptMimetypesFile) === false }"
          @blur="validate('mediaUploadAcceptMimetypesFile')"
        />
        <p
          v-if="checkEmpty(errors.mediaUploadAcceptMimetypesFile) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.mediaUploadAcceptMimetypesFile[0] }}
        </p>
      </div>

      <div class="field mt-5">
        <label class="font-semibold">
          {{ $t('form.mediaUploadSizeLimitMBFile') }}
        </label>
        <InputText
          v-model="mediaUploadSizeLimitMBFile"
          class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
          :class="{ 'p-invalid': checkEmpty(errors.mediaUploadSizeLimitMBFile) === false }"
          @blur="validate('mediaUploadSizeLimitMBFile')"
        />
        <p
          v-if="checkEmpty(errors.mediaUploadSizeLimitMBFile) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.mediaUploadSizeLimitMBFile[0] }}
        </p>
      </div>
    </div>

    <div class="field mb-2">
      <div class="flex align-items-center">
        <label class="checkbox">
          <input
            v-model="functions"
            value="comment"
            type="checkbox"
          />
          {{ $t('term.availableFunctions.comment') }}
        </label>
      </div>
    </div>

    <div
      v-if="functions.includes('comment')"
      class="pl-5 pt-2 pb-4"
    >
      <div class="field">
        <label class="font-semibold">
          {{ $t('form.commentDefaultPublishStatus.label') }}
        </label>
        <FormSelectField
          v-model="commentDefaultPublishStatus"
          :options="commentDefaultPublishStatusOptions"
          :options-label-trans-key="'form.commentDefaultPublishStatus'"
          :default-option-text="$t('msg.pleaseSelect')"
          :is-required="true"
        />
        <p
          v-if="checkEmpty(errors.commentDefaultPublishStatus) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.commentDefaultPublishStatus[0] }}
        </p>
      </div>
    </div>

    <div
      v-if="globalError"
      class="block has-text-danger mt-5 mb-0"
    >
      {{ globalError }}
    </div>

    <div class="field mt-5">
      <div class="control">
        <button
          class="button is-warning"
          :disabled="isLoading || hasErrors"
          @click="save(false)"
          v-text="$t('common.edit')"
        ></button>
      </div>
    </div>

    <div class="field">
      <div class="control">
        <button
          class="button is-light"
          :disabled="isLoading"
          @click="cancel"
          v-text="$t('common.cancel')"
        ></button>
      </div>
    </div>
  </div>
</template>
<script>
import 'primevue/resources/themes/lara-light-indigo/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeflex/primeflex.css'
import InputText from 'primevue/inputtext'

import common from '@/util/common'
import str from '@/util/str'
import config from '@/config/config'
import { Admin } from '@/api'
import { siteMixin } from '@/mixins/site'
import FormSelectField from '@/components/molecules/FormSelectField.vue'

export default {
  components: {
    InputText,
    FormSelectField
  },

  mixins: [siteMixin],

  props: {
    service: {
      type: Object,
      default: null
    }
  },

  data() {
    return {
      serviceIdInput: '',
      label: '',
      functions: [],
      defaultConfigs: [],
      outerSiteUrl: '',
      frontendPostDetailUrlPrefix: '',
      mediaUploadAcceptMimetypesImage: '',
      mediaUploadImageSizes: '',
      mediaUploadSizeLimitMBImage: '',
      mediaUploadAcceptMimetypesFile: '',
      mediaUploadSizeLimitMBFile: '',
      commentDefaultPublishStatus: 'unpublish',
      commentDefaultPublishStatusOptions: ['publish', 'unpublish', 'unconfirm'],
      fieldKeys: [
        'serviceIdInput',
        'label',
        'functions',
        'outerSiteUrl',
        'frontendPostDetailUrlPrefix',
        'mediaUploadAcceptMimetypesImage',
        'mediaUploadImageSizes',
        'mediaUploadSizeLimitMBImage',
        'mediaUploadAcceptMimetypesFile',
        'mediaUploadSizeLimitMBFile',
        'commentDefaultPublishStatus'
      ]
    }
  },

  computed: {
    isEdit() {
      return this.service != null
    },

    isLoading() {
      return this.$store.state.isLoading
    },

    isEmptyAllFields() {
      if (!this.isEdit && !this.checkEmpty(this.serviceIdInput)) return false
      if (!this.checkEmpty(this.label)) return false
      if (!this.checkEmpty(this.outerSiteUrl)) return false
      if (!this.checkEmpty(this.frontendPostDetailUrlPrefix)) return false
      if (!this.checkEmpty(this.mediaUploadAcceptMimetypesImage)) return false
      if (!this.checkEmpty(this.mediaUploadImageSizes)) return false
      if (!this.checkEmpty(this.mediaUploadSizeLimitMBImage)) return false
      if (!this.checkEmpty(this.mediaUploadAcceptMimetypesFile)) return false
      if (!this.checkEmpty(this.mediaUploadSizeLimitMBFile)) return false
      if (!this.checkEmpty(this.commentDefaultPublishStatus)) return false
      return true
    },

    hasErrors() {
      if (this.globalError) return true

      let hasError = false
      Object.keys(this.errors).map((field) => {
        if (this.errors[field].length > 0) hasError = true
      })
      return hasError
    }
  },

  async created() {
    if (this.isEdit) {
      this.setService()
    } else {
      await this.setDefaultConfigs()
      this.resetConfigInputs()
    }
  },

  methods: {
    setService() {
      this.label = this.service.label != null ? String(this.service.label) : ''
      this.functions = this.service.functions != null ? this.service.functions : []
      if (common.checkObjHasProp(this.service, 'configs')) {
        this.outerSiteUrl =
          this.service.configs.outerSiteUrl != null ? String(this.service.configs.outerSiteUrl) : ''
        this.frontendPostDetailUrlPrefix =
          this.service.configs.frontendPostDetailUrlPrefix != null
            ? String(this.service.configs.frontendPostDetailUrlPrefix)
            : ''
        this.mediaUploadAcceptMimetypesImage =
          this.service.configs.mediaUploadAcceptMimetypesImage != null
            ? String(this.service.configs.mediaUploadAcceptMimetypesImage)
            : ''
        this.mediaUploadImageSizes =
          this.service.configs.mediaUploadImageSizes != null
            ? String(this.service.configs.mediaUploadImageSizes)
            : ''
        this.mediaUploadSizeLimitMBImage =
          this.service.configs.mediaUploadSizeLimitMBImage != null
            ? String(this.service.configs.mediaUploadSizeLimitMBImage)
            : ''
        this.mediaUploadAcceptMimetypesFile =
          this.service.configs.mediaUploadAcceptMimetypesFile != null
            ? String(this.service.configs.mediaUploadAcceptMimetypesFile)
            : ''
        this.mediaUploadSizeLimitMBFile =
          this.service.configs.mediaUploadSizeLimitMBFile != null
            ? String(this.service.configs.mediaUploadSizeLimitMBFile)
            : ''
        this.commentDefaultPublishStatus =
          this.service.configs.commentDefaultPublishStatus != null
            ? String(this.service.configs.commentDefaultPublishStatus)
            : this.commentDefaultPublishStatus
      } else {
        this.resetConfigInputs()
      }
    },

    resetInputs() {
      this.serviceIdInput = ''
      this.label = ''
      this.functions = []
      this.resetConfigInputs()
    },

    resetConfigInputs() {
      this.defaultConfigs.map((config) => {
        this[config.configName] = config.configVal.toString()
      })
    },

    async setDefaultConfigs() {
      try {
        this.defaultConfigs = await Admin.getServiceConfigList(this.adminUserToken)
      } catch (err) {
        this.debugOutput(err)
        this.showGlobalMessage(this.$t('msg["Server error"]'))
      }
    },

    async save() {
      this.validateAll()
      if (this.hasErrors) return

      try {
        let vals = {}
        if (!this.isEdit) vals.serviceId = this.serviceIdInput
        vals.label = this.label
        vals.functions = this.functions

        vals.configs = {}
        vals.configs.outerSiteUrl = this.outerSiteUrl
        vals.configs.frontendPostDetailUrlPrefix = this.frontendPostDetailUrlPrefix
        vals.configs.mediaUploadAcceptMimetypesImage = this.mediaUploadAcceptMimetypesImage
        vals.configs.mediaUploadImageSizes = this.mediaUploadImageSizes
        vals.configs.mediaUploadSizeLimitMBImage = this.mediaUploadSizeLimitMBImage
        vals.configs.mediaUploadAcceptMimetypesFile = this.mediaUploadAcceptMimetypesFile
        vals.configs.mediaUploadSizeLimitMBFile = this.mediaUploadSizeLimitMBFile
        vals.configs.commentDefaultPublishStatus = this.commentDefaultPublishStatus

        this.$store.dispatch('setLoading', true)
        if (this.isEdit) {
          await Admin.updateService(this.serviceId, vals, this.adminUserToken)
        } else {
          await Admin.createService(vals, this.adminUserToken)
        }
        this.$store.dispatch('setLoading', false)
        this.resetInputs()
        this.$router.push('/admin/services')
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        const msgKey = this.isEdit ? 'Edit failed' : 'Create failed'
        this.handleApiError(err, this.$t(`msg["${msgKey}"]`))
      }
    },

    async checkServiceIdExists() {
      try {
        this.$store.dispatch('setLoading', true)
        await Admin.checkServiceExists(this.serviceIdInput, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        return true
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        if (err.response == null || err.response.status !== 404) {
          this.handleApiError(err)
        }
        return false
      }
    },

    cancel() {
      this.resetInputs()
      this.$router.push(`/admin/services`)
    },

    validateAll() {
      this.fieldKeys.map((field) => {
        this.validate(field)
      })
      if (this.hasErrors) {
        this.globalError = this.$t("msg['Correct inputs with error']")
      } else if (this.isEmptyAllFields) {
        this.globalError = this.$t("msg['Input required']")
      }
    },

    validate(field) {
      const key = 'validate' + str.capitalize(field)
      if (common.checkObjHasProp(this, key) && typeof this[key] === 'function') {
        this[key]()
      } else {
        this.validateStringFieldCommon(field)
      }
    },

    validateStringFieldCommon(field) {
      this.initError(field)
      if (this[field] === null) this[field] = ''
      if (typeof this[field] === 'string') {
        this[field] = this[field].trim()
      }
    },

    async validateServiceIdInput() {
      if (this.isEdit) return

      this.initError('serviceIdInput')
      if (this.serviceIdInput === null) this.serviceIdInput = ''
      this.serviceIdInput = this.serviceIdInput.trim()
      if (this.checkEmpty(this.serviceIdInput)) {
        this.errors.serviceIdInput.push(this.$t('msg["Input required"]'))
      } else if (str.checkSlug(this.serviceIdInput) === false) {
        this.errors.serviceIdInput.push(this.$t('msg.InvalidInput'))
      } else if (this.isEdit === false || this.serviceIdInput !== this.service.serviceId) {
        const isExists = await this.checkServiceIdExists(this.serviceIdInput)
        if (isExists) {
          this.errors.serviceIdInput.push(this.$t('msg["Already in use"]'))
        }
      }
    },

    validateLabel() {
      this.validateStringFieldCommon('label')
      if (this.checkEmpty(this.label)) this.errors.label.push(this.$t('msg["Input required"]'))
    },

    validateFunctions() {
      const allowed = config.availableFunctions
      this.initError('functions')
      if (this.functions == null) this.functions = []
      if (this.functions) {
        let hasError = false
        this.functions.map((item) => {
          if (hasError === true) return
          if (allowed.includes(item) === false) {
            hasError = true
          }
        })
        if (hasError === true) {
          this.globalError = this.$t('msg.invalidError', { field: this.$t('form.functionToApply') })
        }
      }
    },

    validateDefaultPublishState() {
      this.initError('commentDefaultPublishStatus')
      if (this.commentDefaultPublishStatus === null) this.commentDefaultPublishStatus = ''
      this.commentDefaultPublishStatus = this.commentDefaultPublishStatus.trim()
      if (this.checkEmpty(this.commentDefaultPublishStatus) === false) {
        if (
          this.commentDefaultPublishStatusOptions.includes(this.commentDefaultPublishStatus) ===
          false
        )
          this.errors.commentDefaultPublishStatus.push(this.$t('msg.InvalidInput'))
      }
    }
  }
}
</script>

<template>
  <div>
    <div class="flex-item">
      <div class="field">
        <label class="font-semibold">{{ $t('form.slug') }}</label>
        <div class="p-inputgroup flex-1">
          <InputText
            v-model="slug"
            type="text"
            class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
            :class="{ 'p-invalid': checkEmpty(errors.slug) === false }"
            @blur="validate('slug')"
          />
          <div
            v-if="isEnableSlugAutoSetButton"
            class="control"
          >
            <eb-dropdown position="is-right">
              <template #label>
                <span>{{ $t('term.autoInput') }}</span>
              </template>
              <div class="dropdown-content">
                <a
                  class="dropdown-item"
                  @click="setSlug('date')"
                  >{{ $t('common.date') }}
                </a>
                <a
                  class="dropdown-item"
                  @click="setSlug('randString')"
                  >{{ $t('term.randString') }}
                </a>
              </div>
            </eb-dropdown>
          </div>
        </div>
        <p
          v-if="checkEmpty(errors.slug) === false"
          class="p-error p-2 text-sm"
        >
          {{ errors.slug[0] }}
        </p>
      </div>

      <div class="field mt-6">
        <label class="font-semibold">{{ $t('common.category') }}</label>
        <category-select v-model="category"></category-select>
      </div>
    </div>

    <div class="field mt-6">
      <label class="font-semibold">{{ $t('form.title') }}</label>
      <InputText
        v-model="title"
        type="text"
        class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
        :class="{ 'p-invalid': checkEmpty(errors.title) === false }"
        @blur="validate('title')"
      />
      <p
        v-if="checkEmpty(errors.title) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.title[0] }}
      </p>
    </div>

    <div class="field mt-6">
      <label class="font-semibold">{{ $t('form.body') }}</label>
      <div>
        <Dropdown
          v-model="editorMode"
          :options="editorModeOptions"
          option-value="code"
          option-label="name"
          class="w-full md:w-14rem"
          :disabled="editorMode.mode === 'richText' && isEnabledRichText === false"
          :class="{ 'p-invalid': checkEmpty(errors.editorMode) === false }"
        />
      </div>
      <p
        v-if="checkEmpty(errors.editorMode) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.editorMode[0] }}
      </p>
    </div>

    <div class="field mt-6">
      <rich-text-editor
        v-if="isEnabledRichText && editorMode === 'richText'"
        :value="body"
        :editor-merge-options="richTextEditorOptions"
        @input="body = $event"
      ></rich-text-editor>

      <MdEditor
        v-else-if="editorMode === 'markdown'"
        v-model="body"
        language="en-US"
      />
      <JsonEditorVue
        v-else-if="editorMode === 'json'"
        v-model="body"
        v-bind="{ mode: 'text', mainMenuBar: false }"
      />

      <NormalTextarea
        v-else
        ref="inputBody"
        v-model="body"
        rows="7"
        auto-resize
        class="w-full"
        @blur="validate('body')"
      />
    </div>

    <div class="field mt-6">
      <label class="font-semibold">{{ $t('common.images') }}</label>
      <FileUploader
        v-if="uploaderOptions"
        v-model="images"
        file-type="image"
        :image-action-button-type="editorMode === 'markdown' ? 'copy' : 'insert'"
        :uploader-options="uploaderOptions.image"
        @insert-image="insertImage"
      />
      <p
        v-if="checkEmpty(errors.images) === false"
        class="p-error p-2 text-sm"
        v-text="checkEmpty(errors.images) ? '' : $t('msg.ErrorsExist')"
      ></p>
    </div>

    <div class="field mt-6">
      <label class="font-semibold">{{ $t('form.files') }}</label>
      <file-uploader
        v-if="uploaderOptions"
        v-model="files"
        file-type="file"
        :uploader-options="uploaderOptions.file"
        @copy-url="copyUrl"
      ></file-uploader>
      <p
        v-if="checkEmpty(errors.files) === false"
        class="p-error p-2 text-sm"
        v-text="checkEmpty(errors.files) ? '' : $t('msg.ErrorsExist')"
      ></p>
    </div>

    <div class="field mt-6">
      <label class="font-semibold">{{ $t('common.link') }}</label>
      <ul v-if="links.length > 0">
        <li
          v-for="link in links"
          :key="link.id"
        >
          <link-inputs
            :link="link"
            @updated-link="updateLink"
            @delete="deleteLink"
            @has-error="setLinksError"
          ></link-inputs>
        </li>
      </ul>
      <p
        v-if="checkEmpty(errors.links) === false"
        class="p-error p-2 text-sm"
        v-text="checkEmpty(errors.links) ? '' : $t('msg.ErrorsExist')"
      ></p>
    </div>
    <div class="field">
      <button
        class="button"
        :disabled="isAddLinkBtnEnabled === false"
        @click="addLink"
      >
        <span class="icon">
          <i class="fas fa-link"></i>
        </span>
        <span>{{ $t('common.addFor', { target: $t('common.link') }) }}</span>
      </button>
    </div>

    <div class="field mt-6">
      <label class="font-semibold">{{ $t('common.tag') }}</label>
      <div class="control">
        <EbTagsInput
          :tags="tags"
          :existed-tags="savedTags"
          @updated="updateTags"
        />
      </div>

      <p
        v-if="checkEmpty(errors.tags) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.tags[0] }}
      </p>
    </div>

    <div class="field mt-6">
      <label class="font-semibold">{{ $t('common.publishAt') }}</label>
      <DatePicker v-model="publishAt" />
      <p
        v-if="checkEmpty(errors.publishAt) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.publishAt[0] }}
      </p>
      <p class="help text-warning-600">{{ $t('post.msg.publishAtCaution') }}</p>
    </div>

    <div class="field mt-6">
      <label class="font-semibold">{{ $t('common.dispSetting') }}</label>
      <div class="flex align-items-center">
        <label class="checkbox">
          <input
            v-model="isHiddenInList"
            :value="true"
            type="checkbox"
          />
          {{ $t('form.hideInList') }}
        </label>
      </div>
    </div>

    <div
      v-if="globalError"
      class="block has-text-danger mt-6"
    >
      {{ globalError }}
    </div>

    <div class="field mt-6">
      <div
        v-if="!isPublished"
        class="control"
      >
        <button
          class="button is-info"
          :disabled="isLoading || hasErrors"
          @click="save(false)"
          v-text="$t('common.saveDraft')"
        ></button>
      </div>

      <div
        v-else
        class="control"
      >
        <button
          class="button is-warning"
          :disabled="isLoading || hasErrors"
          @click="save(false)"
          v-text="$t('common.doUpdate')"
        ></button>
      </div>
    </div>

    <div class="field">
      <div
        v-if="!isPublished"
        class="control"
      >
        <button
          class="button is-warning"
          :disabled="isLoading || hasErrors"
          @click="save(true)"
          v-text="$t('common.publish')"
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
import NormalTextarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'

import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

import { getTinymce } from '@tinymce/tinymce-vue/lib/cjs/main/ts/TinyMCE'
import str from '@/util/str'
import obj from '@/util/obj'
import utilDate from '@/util/date'
import utilMedia from '@/util/media'
import { Admin, Tag } from '@/api'
import config from '@/config/config'
import serviceConfig from '@/config/serviceConfig'
import RichTextEditor from '@/components/atoms/RichTextEditor'
import FileUploader from '@/components/organisms/FileUploader'
import LinkInputs from '@/components/molecules/LinkInputs'
import EbTagsInput from '@/components/molecules/EbTagsInput'
import CategorySelect from '@/components/molecules/CategorySelect'
import EbDropdown from '@/components/molecules/EbDropdown'
import DatePicker from '@/components/molecules/DatePicker'
import { siteMixin } from '@/mixins/site'
import * as bulmaToast from 'bulma-toast'
import { copyText } from 'vue3-clipboard'
import JsonEditorVue from 'json-editor-vue'

export default {
  components: {
    FileUploader,
    LinkInputs,
    EbTagsInput,
    RichTextEditor,
    MdEditor,
    CategorySelect,
    EbDropdown,
    InputText,
    NormalTextarea,
    Dropdown,
    DatePicker,
    JsonEditorVue
  },

  mixins: [siteMixin],

  props: {
    post: {
      type: Object,
      default: null
    }
  },

  emits: ['posted'],

  data() {
    return {
      slug: '',
      category: '',
      title: '',
      images: [],
      files: [],
      links: [],
      body: '',
      editorMode: '',
      tags: [],
      publishAt: '',
      isHiddenInList: false,
      fieldKeys: [
        'slug',
        'category',
        'title',
        'images',
        'files',
        'links',
        'editorMode',
        'body',
        'tags',
        'publishAt',
        'isHiddenInList'
      ],
      savedTags: [],
      errors: [],
      uploaderOptions: null,
      editorModes: [
        {
          mode: 'richText',
          format: 'html'
        },
        {
          mode: 'markdown',
          format: 'markdown'
        },
        {
          mode: 'text',
          format: 'text'
        },
        {
          mode: 'rawHtml',
          format: 'html'
        },
        {
          mode: 'json',
          format: 'json'
        }
      ],
      jsonEditorOptions: {
        mode: 'code',
        onEditable: function () {
          return true
        }
      }
    }
  },

  computed: {
    isLoading() {
      return this.$store.state.isLoading
    },

    isEdit() {
      return this.post != null
    },

    isPublished() {
      if (this.isEdit === false) return false
      return this.post.postStatus === 'publish'
    },

    categoryQuery() {
      const defaultValue = ''
      if (!this.$route.query.category) return defaultValue
      return this.$route.query.category
    },

    isAddLinkBtnEnabled() {
      if (this.checkEmpty(this.errors.links) === false) return false
      if (this.checkEmpty(this.links)) return true
      for (let i = 0, n = this.links.length; i < n; i++) {
        if (this.links[i].url.length === 0) return false
      }
      return true
    },

    isEmptyRequiredFields() {
      if (!this.checkEmpty(this.slug)) return false
      if (!this.checkEmpty(this.title)) return false
      return true
    },

    hasErrors() {
      if (this.globalError) return true

      let hasError = false
      Object.keys(this.errors).map((field) => {
        if (this.errors[field].length > 0) hasError = true
      })
      return hasError
    },

    isEnabledRichText() {
      return Boolean(config.tinyMCEApiKey)
    },

    bodyFormat() {
      return this.getFormatByMode(this.editorMode)
    },

    isEnableSlugAutoSetButton() {
      return obj.getVal(config.post, 'isEnableSlugAutoSetButton', false)
    },

    postsPageUriObj() {
      const path = `/admin/posts/${this.serviceId}`
      const query = this.$store.getters.adminPostsPagerQueryCurrent(true)
      return { path: path, query: query }
    },

    editorModeOptions() {
      const options = []
      this.editorModes.map((mode) => {
        options.push({
          name: this.$t(`term['${mode.mode}']`),
          code: mode.mode
        })
      })
      return options
    },

    richTextEditorOptions() {
      if (serviceConfig[this.serviceId] == null) return {}
      return serviceConfig[this.serviceId].richTextEditorOptions
    }
  },

  watch: {
    images() {
      this.initError('images')
    },

    files() {
      this.initError('files')
    },

    links() {
      this.initError('links')
    },

    body() {
      if (this.bodyFormat === 'json') {
        this.initError('body')
      }
    },

    editorMode(val, oldVal) {
      if (!oldVal) return
      this.setBody()
    }
  },

  async created() {
    this.initErrors(this.fieldKeys)
    this.setEditorMode()
    if (this.isEnabledRichText === false) this.editorMode = 'text'
    if (this.isEdit === true) {
      this.setPost()
    } else {
      if (this.categoryQuery) {
        this.category = this.categoryQuery
      }
      if (config.post.autoSlugSet.isEnabled === true) {
        this.setSlug(config.post.autoSlugSet.format)
      }
    }
    this.setUploaderOptions()
    this.setTags()
  },

  methods: {
    setEditorMode() {
      this.editorMode = 'richText'
      if (this.checkObjHasProp(config.post, 'defaultEditorMode', true)) {
        this.editorMode = config.post.defaultEditorMode
      }
      if (this.editorMode === 'richText' && this.isEnabledRichText === false) {
        this.editorMode = 'text'
      }
    },

    setPost() {
      this.slug = this.post.slug != null ? String(this.post.slug) : ''
      this.category =
        'category' in this.post && this.post.category && this.post.category.slug != null
          ? String(this.post.category.slug)
          : ''
      this.title = this.post.title != null ? String(this.post.title) : ''
      this.images = this.post.images != null ? this.post.images : []
      this.files = this.post.files != null ? this.post.files : []
      this.links = this.post.links != null ? this.post.links : []
      this.editorMode = this.getModeByFormat(this.post.bodyFormat)
      this.tags = []
      if (this.checkEmpty(this.post.tags) === false) {
        this.tags = this.post.tags.map((tag) => {
          tag.value = tag.label
          return tag
        })
      }
      this.publishAt =
        this.post.publishAt && this.post.publishAt !== 'None' ? this.post.publishAt : ''
      if (this.post.bodyFormat === 'json') {
        this.body = this.post.body != null ? JSON.parse(this.post.body) : {}
      } else {
        this.body = this.post.body != null ? String(this.post.body) : ''
      }
      this.isHiddenInList = this.post.isHiddenInList
    },

    setBody() {
      const defBody = this.isEdit ? this.post.body : ''
      if (this.bodyFormat === 'json' && typeof this.body === 'string') {
        this.body = str.checkJson(this.body) ? JSON.parse(this.body) : {}
      } else if (this.bodyFormat !== 'json' && typeof this.body !== 'string') {
        this.body = defBody
      }
    },

    async setSlug(format) {
      this.initError('slug')
      try {
        let slug
        let isNotExists = false

        for (let i = 0, n = 10; i < n; i++) {
          if (isNotExists === true) break

          if (format === 'randString') {
            slug = str.getRandStr(11)
          } else {
            slug = this.getSlugAsDateFormat(slug)
          }
          isNotExists = await this.checkSlugNotExists(slug)
        }
        if (isNotExists === false) {
          throw new Error('Create Slug Failed')
        }
        this.slug = slug
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async setTags() {
      try {
        const res = await Tag.getAll(this.serviceId)
        if (res.items.length > 0) {
          this.savedTags = res.items
        }
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async setUploaderOptions() {
      try {
        const res = await Admin.getServices(this.serviceId, null, this.adminUserToken)
        this.uploaderOptions = {
          image: {
            sizes: res.configs.mediaUploadImageSizes,
            mimeTypes: res.configs.mediaUploadAcceptMimetypesImage,
            extensions: [],
            sizeLimitMB: res.configs.mediaUploadSizeLimitMBImage
          },
          file: {
            mimeTypes: res.configs.mediaUploadAcceptMimetypesFile,
            extensions: [],
            sizeLimitMB: res.configs.mediaUploadSizeLimitMBFile
          }
        }
        res.configs.mediaUploadAcceptMimetypesImage.map((item) => {
          let ext = utilMedia.getExtensionByMimetype(item)
          this.uploaderOptions.image.extensions.push(ext)
        })
        res.configs.mediaUploadAcceptMimetypesFile.map((item) => {
          let ext = utilMedia.getExtensionByMimetype(item)
          this.uploaderOptions.image.extensions.push(ext)
        })
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    resetInputs() {
      this.slug = ''
      this.category = ''
      this.title = ''
      if (this.editorMode !== 'richText') {
        this.body = ''
      }
      this.images = []
      this.files = []
      this.links = []
      this.tags = []
      this.publishAt = ''
      this.isHiddenInList = false
    },

    async save(forcePublish = false) {
      this.validateAll()
      if (this.hasErrors) return
      try {
        let vals = {}
        vals.slug = this.slug
        vals.category = this.category
        vals.title = this.title
        vals.bodyFormat = this.bodyFormat
        vals.images = this.images
        vals.files = this.files
        vals.links = this.links
        vals.isHiddenInList = this.isHiddenInList
        vals.publishAt = this.publishAt
        if (this.bodyFormat === 'json' && typeof this.body === 'object') {
          vals.body = JSON.stringify(this.body)
        } else {
          vals.body = this.body
        }

        vals.tags = []
        this.tags.map((tag) => {
          if ('tagId' in tag) {
            vals.tags.push({ tagId: tag.tagId })
          } else {
            vals.tags.push({ label: tag.value })
          }
        })

        if (forcePublish) {
          vals.status = 'publish'
        } else {
          if (this.isEdit === false) vals.status = 'unpublish'
        }
        this.$store.dispatch('setLoading', true)
        await this.checkAndRefreshTokens()
        let res
        if (this.isEdit) {
          res = await Admin.updatePost(this.serviceId, this.post.postId, vals, this.adminUserToken)
        } else {
          res = await Admin.createPost(this.serviceId, vals, this.adminUserToken)
          this.$store.dispatch('resetAdminPostsPager', false)
        }
        this.$store.dispatch('setAdminPostList', null)
        this.$store.dispatch('setLoading', false)
        this.$emit('posted', res)
        this.resetInputs()
        this.$router.push(`/admin/posts/${this.serviceId}/${res.postId}`)
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

    async checkSlugNotExists(slug) {
      try {
        this.$store.dispatch('setLoading', true)
        await this.checkAndRefreshTokens()
        const res = await Admin.checkPostSlugNotExists(this.serviceId, slug, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        return res
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err)
      }
    },

    cancel() {
      this.resetInputs()
      this.$router.push(this.postsPageUriObj)
    },

    handleJsonEditorError() {
      this.initError('body')
      this.errors.body.push(this.$t('msg.ErrorsExist'))
      // console.log(ev)
    },

    validateAll() {
      this.fieldKeys.map((field) => {
        this.validate(field)
      })
      if (this.hasErrors) {
        this.globalError = this.$t("msg['Correct inputs with error']")
      } else if (this.isEmptyRequiredFields) {
        this.globalError = this.$t("msg['Input required']")
      }
    },

    validate(field) {
      const key = 'validate' + str.capitalize(field)
      this[key]()
    },

    async validateSlug() {
      this.initError('slug')
      if (this.slug === null) this.slug = ''
      this.slug = this.slug.trim()
      if (this.checkEmpty(this.slug)) {
        this.errors.slug.push(this.$t('msg["Input required"]'))
      } else if (str.checkSlug(this.slug, true) === false) {
        this.errors.slug.push(this.$t('msg.InvalidInput'))
      } else if (this.isEdit === false || this.slug !== this.post.slug) {
        const isNotExists = await this.checkSlugNotExists(this.slug)
        if (isNotExists === false) {
          this.errors.slug.push(this.$t('msg["Already in use"]'))
        }
      }
    },

    async validateCategory() {
      this.initError('category')
      if (this.category === null) this.category = ''
      this.category = this.category.trim()
      if (!this.checkEmpty(this.category) && str.checkSlug(this.category) === false) {
        this.errors.category.push(this.$t('msg.InvalidInput'))
      }
    },

    validateTitle() {
      this.initError('title')
      if (this.title === null) this.title = ''
      this.title = this.title.trim()
      if (this.checkEmpty(this.title)) this.errors.title.push(this.$t('msg["Input required"]'))
    },

    validateBody() {
      this.initError('body')
      if (this.body === null) {
        if (this.bodyFormat === 'json') {
          this.body = {}
        } else {
          this.body = ''
        }
      }
      if (this.bodyFormat === 'json') {
        if (typeof this.body === 'string' && !str.checkJson(this.body)) {
          this.errors['body'].push(this.$t('msg.InvalidInput'))
        }
      } else {
        this.body = this.body.trimEnd()
      }
      //if (this.checkEmpty(this.body)) this.errors.body.push(this.$t('msg["Input required"]'))
    },

    validateImages() {
      this.initError('images')
      if (this.images === null) this.images = []
    },

    validateFiles() {
      this.initError('files')
      if (this.files === null) this.files = []
    },

    validateLinks() {
      this.initError('links')
      if (this.links === null) this.links = []
      if (this.links.length > 0) {
        for (let i = 0, n = this.links.length; i < n; i++) {
          if (this.checkEmpty(this.links[i].url)) {
            if (this.checkEmpty(this.links[i].label)) {
              this.links.splice(i, 1)
            } else {
              this.errors.links.push('hasError')
            }
          }
        }
      }
    },

    validateEditorMode() {
      this.initError('editorMode')
      if (this.checkEmpty(this.editorMode)) {
        this.errors.editorMode.push(this.$t('msg["Input required"]'))
      } else if (this.editorModes.find((item) => item.mode === this.editorMode) == null) {
        this.errors.editorMode.push(this.$t('msg.InvalidInput'))
      }
    },

    validateTags() {
      this.initError('tags')
      this.tags.map((val) => {
        //if (typeof val !== 'string') return
        if (this.savedTags.find((saved) => saved.label === val) != null) {
          this.errors.tags.push(this.$t('msg.duplicated'))
        }
      })
    },

    validatePublishAt() {
      this.initError('publishAt')
    },

    validateIsHiddenInList() {
      this.initError('isHiddenInList')
    },

    insertImage(payload) {
      const imgUrl = payload.url
      let imgTag
      if (this.editorMode === 'markdown') {
        const altText = payload.caption ? payload.caption : this.$t('common.image')
        imgTag = `![${altText}](${imgUrl})`
      } else if (this.editorMode === 'text') {
        imgTag = imgUrl
      } else {
        let attrs = ['img', `src="${imgUrl}"`]
        if (payload.caption) attrs.push(`alt="${payload.caption}"`)
        imgTag = '<' + attrs.join(' ') + '>'
      }

      if (['text', 'rawHtml'].includes(this.editorMode)) {
        const inputEl = this.$refs.inputBody.$el.getElementsByTagName('textarea')[0]
        const inputPos = inputEl.selectionStart
        const preVal = this.body.substr(0, inputPos)
        const postVal = this.body.substr(inputPos)
        this.body = `${preVal}${imgTag}${postVal}`
      } else if (this.editorMode === 'richText') {
        getTinymce().activeEditor.insertContent(imgTag)
      } else if (this.editorMode === 'markdown') {
        copyText(imgTag, undefined, (error) => {
          let msg, type
          if (error) {
            this.debugOutput(error)
            msg = this.$t('msg.copyFailed')
            type = 'is-danger'
          } else {
            msg = this.$t('msg.copied')
            type = 'is-success'
          }
          bulmaToast.toast({
            message: msg,
            type: type,
            position: 'bottom-center',
            dismissible: true,
            opacity: 0.9,
            duration: 5000,
            aimate: { in: 'fadeInUp', out: 'fadeOutDown' },
            extraClasses: 'u-min-width-400'
          })
        })
      } else {
        this.body += `\n${imgTag}`
      }
    },

    copyUrl(payload) {
      const fileUrl = payload.url
      copyText(fileUrl, undefined, (error) => {
        let msg, type
        if (error) {
          this.debugOutput(error)
          msg = this.$t('msg.copyFailed')
          type = 'is-danger'
        } else {
          msg = this.$t('msg.copied')
          type = 'is-success'
        }
        bulmaToast.toast({
          message: msg,
          type: type,
          position: 'bottom-center',
          dismissible: true,
          opacity: 0.9,
          duration: 5000,
          aimate: { in: 'fadeInUp', out: 'fadeOutDown' },
          extraClasses: 'u-min-width-400'
        })
      })
    },

    addLink() {
      let maxId = 0
      if (this.links.length > 0) {
        maxId = this.links.reduce((a, b) => (a.id > b.id ? a : b)).id
      }
      this.links.push({ id: maxId + 1, url: '', label: '' })
    },

    setLinksError(hasError) {
      if (hasError === false) {
        this.errors.links = []
      } else {
        this.errors.links.push('hasError')
      }
    },

    updateLink(payload) {
      const index = this.links.findIndex((item) => {
        return item.id === payload.id
      })
      this.links.splice(index, 1, payload)
    },

    deleteLink(id) {
      const index = this.links.findIndex((item) => {
        return item.id === id
      })
      this.links.splice(index, 1)

      if (this.links.length === 0) {
        this.initError('links')
      }
    },

    updateTags(e) {
      this.tags = e
      this.validate('tags')
    },

    getModeByFormat(format) {
      const res = this.editorModes.find((item) => item.format === format)
      if (res == null) return ''
      return res.mode
    },

    getFormatByMode(mode) {
      const res = this.editorModes.find((item) => item.mode === mode)
      if (res == null) return ''
      return res.format
    },

    getSlugAsDateFormat(current) {
      const suffixes = 'abcdefghijklmnopqrstuvwxyz'.split('')
      const today = utilDate.currentStr('yyMMdd')
      if (!current) return today
      if (current === today) return today + suffixes[0]

      let currentSuffix = current.replace(today, '')
      const index = suffixes.indexOf(currentSuffix)
      if (index === -1) {
        throw new Error('Current slug is invalid')
      } else if (index + 1 > suffixes.length - 1) {
        throw new Error('Create Slug Failed')
      }
      return today + suffixes[index + 1]
    }
  }
}
</script>
<style>
.flex-item {
  flex: 1;
}
.p-dropdown-item {
  padding: 0.5rem 1rem;
}
.text-warning-600 {
  color: #d97706;
}
</style>

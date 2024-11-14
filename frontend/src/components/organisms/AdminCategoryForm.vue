<template>
  <div>
    <div class="field">
      <label class="is-block has-text-weight-semibold mb-2">{{
        $t('common.parentCategory')
      }}</label>
      <category-select v-model="parentCategorySlug"></category-select>
      <p
        v-if="checkEmpty(errors.parentCategorySlug) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.parentCategorySlug[0] }}
      </p>
    </div>

    <div class="field mt-5">
      <label class="font-semibold">{{ $t('form.slug') }}</label>
      <div v-if="isEdit">
        {{ category.slug }}
      </div>
      <InputText
        v-else
        type="text"
        v-model="slug"
        @blur="validate('slug')"
        class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
        :class="{ 'p-invalid': checkEmpty(errors.slug) === false }"
      />
      <p
        v-if="checkEmpty(errors.slug) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.slug[0] }}
      </p>
    </div>

    <div class="field mt-5">
      <label class="font-semibold">{{ $t('form.label') }}</label>
      <InputText
        type="text"
        v-model="label"
        @blur="validate('label')"
        class="text-base text-color surface-overlay p-2 border-1 border-solid surface-border border-round appearance-none outline-none focus:border-primary w-full"
        :class="{ 'p-invalid': checkEmpty(errors.label) === false }"
      />
      <p
        v-if="checkEmpty(errors.label) === false"
        class="p-error p-2 text-sm"
      >
        {{ errors.label[0] }}
      </p>
    </div>

    <div class="field mt-5">
      <div class="control">
        <button
          class="button is-info"
          :disabled="isLoading || hasErrors"
          @click="save(true)"
          v-text="isEdit ? $t('common.edit') : $t('common.add')"
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

import str from '@/util/str'
import obj from '@/util/obj'
import { Admin } from '@/api'
import CategorySelect from '@/components/molecules/CategorySelect'
import { siteMixin } from '@/mixins/site'

export default {
  components: {
    CategorySelect,
    InputText
  },

  mixins: [siteMixin],

  props: {
    category: {
      type: Object,
      required: false,
      default: null
    },

    parentCategorySlugDefault: {
      type: String,
      required: false,
      default: ''
    },

    isModalIncludes: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      slug: '',
      label: '',
      parentCategorySlug: '',
      fieldKeys: ['slug', 'label', 'parentCategorySlug']
    }
  },

  computed: {
    isEdit() {
      return this.category != null
    },

    isLoading() {
      return this.$store.state.isLoading
    },

    isEmptyRequiredFields() {
      if (!this.checkEmpty(this.slug)) return false
      if (!this.checkEmpty(this.label)) return false
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

  watch: {
    parentCategorySlug(val) {
      this.initError('parentCategorySlug')
    }
  },

  async created() {
    if (this.isEdit === true) {
      this.setCategory()
    } else {
      if (this.parentCategorySlugDefault) {
        this.parentCategorySlug = this.parentCategorySlugDefault
      }
    }
  },

  methods: {
    setCategory() {
      this.slug = this.category.slug != null ? String(this.category.slug) : ''
      this.label =
        this.category.label != null ? String(this.category.label) : ''
      if (obj.checkObjHasProp(this.category, 'parents', true)) {
        let parents = this.category.parents
        parents.sort((a, b) => {
          if (a.parentPath < b.parentPath) {
            return -1
          }
          if (a.parentPath > b.parentPath) {
            return 1
          }
          return 0
        })
        const parentCate = parents.slice(-1)[0]
        this.parentCategorySlug = parentCate.slug
      }
    },

    resetInputs() {
      this.slug = ''
      this.label = ''
    },

    async save() {
      this.validateAll()
      if (this.hasErrors) return

      try {
        let vals = {}
        vals.label = this.label
        vals.parentCategorySlug = this.parentCategorySlug
        if (this.isEdit === false) vals.slug = this.slug

        this.$store.dispatch('setLoading', true)
        let res
        if (this.isEdit) {
          res = await Admin.updateCategory(
            this.serviceId,
            this.slug,
            vals,
            this.adminUserToken
          )
        } else {
          res = await Admin.createCategory(
            this.serviceId,
            vals,
            this.adminUserToken
          )
        }
        this.$store.dispatch('setLoading', false)
        this.$emit('posted', res)
        this.cancel()
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

    cancel() {
      this.resetInputs()
      if (this.isModalIncludes) {
        this.$emit('close')
      } else {
        this.$router.push(`/admin/categories/${this.serviceId}`)
      }
    },

    async checkSlugNotExists(slug) {
      try {
        this.$store.dispatch('setLoading', true)
        const res = await Admin.checkCategorySlugNotExists(
          this.serviceId,
          slug,
          this.adminUserToken
        )
        this.$store.dispatch('setLoading', false)
        return res
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err)
      }
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
      } else if (str.checkSlug(this.slug) === false) {
        this.errors.slug.push(this.$t('msg.InvalidInput'))
      } else if (this.isEdit === false || this.slug !== this.category.slug) {
        const isNotExists = await this.checkSlugNotExists(this.slug)
        if (isNotExists === false) {
          this.errors.slug.push(this.$t('msg["Already in use"]'))
        }
      }
    },

    async validateParentCategorySlug() {
      this.initError('parentCategorySlug')
      if (this.parentCategorySlug === null) this.parentCategorySlug = ''
      this.parentCategorySlug = this.parentCategorySlug.trim()
      if (
        !this.checkEmpty(this.parentCategorySlug) &&
        str.checkSlug(this.parentCategorySlug) === false
      ) {
        this.errors.parentCategorySlug.push(this.$t('msg.InvalidInput'))
      } else if (this.parentCategorySlug === this.slug) {
        this.errors.parentCategorySlug.push(
          this.$t('msg.inputDifferentValueFrom', {
            target: this.$t('form.slug')
          })
        )
      }
    },

    validateLabel() {
      this.initError('label')
      if (this.label === null) this.label = ''
      this.label = this.label.trim()
      if (this.checkEmpty(this.label))
        this.errors.label.push(this.$t('msg["Input required"]'))
    }
  }
}
</script>

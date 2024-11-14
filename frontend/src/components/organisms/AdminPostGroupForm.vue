<template>
  <div>
    <div class="field">
      <label class="font-semibold">{{ $t('form.slug') }}</label>
      <div v-if="isEdit">
        {{ this.slug }}
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
      <label class="font-semibold">{{ $t('common.dispLabel') }}</label>
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

    <div
      v-if="globalError"
      class="block has-text-danger mt-5"
    >
      {{ globalError }}
    </div>

    <div class="field mt-5">
      <div class="control">
        <button
          class="button is-info"
          :disabled="isLoading || hasErrors"
          @click="save()"
          v-text="isEdit ? $t('common.edit') : $t('common.create')"
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
import { Admin } from '@/api'
import { siteMixin } from '@/mixins/site'

export default {
  mixins: [siteMixin],

  components: {
    InputText
  },

  props: {
    group: {
      type: Object,
      default: null
    }
  },

  data() {
    return {
      slug: '',
      label: '',
      fieldKeys: ['slug', 'label'],
      errors: []
    }
  },

  computed: {
    isEdit() {
      return this.group != null
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

  watch: {},

  async created() {
    if (this.isEdit === true) {
      await this.setPostGroup()
    }
  },

  methods: {
    setPostGroup() {
      this.slug = this.group.slug != null ? String(this.group.slug) : ''
      this.label = this.group.label != null ? String(this.group.label) : ''
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
        vals.slug = this.slug
        vals.label = this.label

        this.$store.dispatch('setLoading', true)
        let res
        if (this.isEdit) {
          res = await Admin.updatePostGroup(
            this.serviceId,
            this.group.slug,
            vals,
            this.adminUserToken
          )
        } else {
          res = await Admin.createPostGroup(this.serviceId, vals, this.adminUserToken)
        }
        this.$store.dispatch('setLoading', false)
        this.$emit('posted', res)
        this.resetInputs()
        this.$router.push(`/admin/posts/${this.serviceId}/groups/${vals.slug}`)
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
        const res = await Admin.checkPostGroupSlugNotExists(
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

    cancel() {
      this.resetInputs()
      const backPathSuffix = this.isEdit ? this.slug : ''
      this.$router.push(`/admin/posts/${this.serviceId}/groups/${backPathSuffix}`)
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
      } else if (this.isEdit === false || this.slug !== this.group.slug) {
        const isNotExists = await this.checkSlugNotExists(this.slug)
        if (isNotExists === false) {
          this.errors.slug.push(this.$t('msg["Already in use"]'))
        }
      }
    },

    validateLabel() {
      this.initError('label')
      if (this.label === null) this.label = ''
      this.label = this.label.trim()
      if (this.checkEmpty(this.label)) this.errors.label.push(this.$t('msg["Input required"]'))
    }
  }
}
</script>

<template>
  <div class="card">
    <header
      class="card-header u-clickable"
      @click="isFilterActive = !isFilterActive"
    >
      <p class="card-header-title">
        {{ $t('form.specifyingFilterConditions') }}
      </p>
      <button
        class="card-header-icon"
        aria-label="more options"
      >
        <span class="icon">
          <i
            class="fas"
            :class="{ 'fa-angle-down': !isFilterActive, 'fa-angle-up': isFilterActive }"
            aria-hidden="true"
          ></i>
        </span>
      </button>
    </header>

    <div
      v-if="isFilterActive"
      class="card-content"
    >
      <div class="content pb-3">
        <p class="is-size-7 mb-5 has-text-warning-dark">
          {{ $t('shortenUrl.msg.restrictionsForFilterConditions') }}
        </p>
        <label class="label">{{ $t('shortenUrl.form.fieldLabelUrlFilter') }}</label>
        <div class="field has-addons">
          <div class="control is-expanded">
            <input
              v-model="inputUrl"
              class="input"
              type="text"
              placeholder="https://example.com"
              @blur="validateUrl"
              @keyup.enter="executeFilterUrl"
            />
          </div>
          <div class="control">
            <button
              class="button is-info"
              @click="executeFilterUrl"
            >
              {{ $t('common.execFilter') }}
            </button>
          </div>
        </div>
        <p
          v-if="urlError"
          class="help is-danger"
        >
          {{ urlError }}
        </p>

        <div class="field mt-5">
          <div class="control">
            <label class="checkbox">
              <input
                v-model="isUnconfirmed"
                :value="true"
                type="checkbox"
                class="mr-2"
                @change="executeFilterUnconfirmed"
              />
              <span class="is-size-6 has-text-weight-semibold">
                {{ $t('shortenUrl.form.fieldItemLabelStatusFilter') }}
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import utilStr from '@/util/str'
import AdminPostsTableRow from '@/components/organisms/AdminPostsTableRow'
import BSelect from '@/components/atoms/BSelect'
import BField from '@/components/molecules/BField'
import BInput from '@/components/atoms/BInput'
import CategorySelect from '@/components/molecules/CategorySelect'
import { siteMixin } from '@/mixins/site'

export default {
  mixins: [siteMixin],

  components: {
    AdminPostsTableRow,
    BSelect,
    BField,
    BInput,
    CategorySelect
  },

  props: {
    url: {
      type: String,
      default: ''
    },
    confirmStatus: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      isFilterActive: false,
      inputUrl: '',
      urlError: '',
      isUnconfirmed: false
    }
  },

  computed: {
    hasFilterQuery() {
      return this.url || this.confirmStatus
    }
  },

  watch: {
    url(val) {
      this.inputUrl = val
    },

    confirmStatus(val) {
      this.isUnconfirmed = val === 'unconfirmed'
    },

    hasFilterQuery(val) {
      if (!this.isFilterActive && val) {
        this.isFilterActive = true
      }
    }
  },

  async created() {
    this.inputUrl = this.url
    this.isUnconfirmed = this.confirmStatus === 'unconfirmed'
    if (this.hasFilterQuery) {
      this.isFilterActive = true
    }
  },

  methods: {
    executeFilterUrl() {
      this.validateUrl()
      if (this.urlError) return
      this.$emit('set-url', this.inputUrl)
    },

    executeFilterUnconfirmed() {
      const status = this.isUnconfirmed ? 'unconfirmed' : 'confirmed'
      this.$emit('set-confirm-status', status)
    },

    validateUrl() {
      this.urlError = ''
      if (this.inputUrl === null) this.inputUrl = ''
      this.inputUrl = this.inputUrl.trim()
      if (this.inputUrl && utilStr.checkStartWithHttpScheme(this.inputUrl) === false) {
        this.urlError = this.$t('msg.InvalidInput')
      }
    }
  }
}
</script>

<style scoped>
#filter-value {
  width: 100%;
}
</style>

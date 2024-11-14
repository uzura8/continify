<template>
  <div>
    <div>
      <InputRequiredSymbol />
      <span class="ml-2">{{ $t('form.required') }}</span>
    </div>
    <div class="field mt-6">
      <label class="label">
        {{ $t('common.locationTo') }}
        <InputRequiredSymbol />
      </label>
      <div class="control">
        <input
          type="text"
          v-model="url"
          @blur="validate('url')"
          class="input"
          :class="{ 'is-danger': checkEmpty(errors.url) === false }"
          placeholder="https://example.com/"
        />
      </div>
      <p
        v-if="checkEmpty(errors.url) === false"
        class="help is-danger"
      >
        {{ errors.url[0] }}
      </p>
    </div>

    <!-- <div class="field mt-6">
      <label class="label">{{ $t('common.name') }}</label>
      <div class="control">
        <input
          type="text"
          v-model="name"
          @blur="validate('name')"
          class="input"
          :class="{ 'is-danger': checkEmpty(errors.name) === false }"
        />
      </div>
      <p
        v-if="checkEmpty(errors.name) === false"
        class="help is-danger"
      >
        {{ errors.name[0] }}
      </p>
    </div> -->

    <div class="field mt-5">
      <label class="label">{{ $t('common.memo') }}</label>
      <div class="control">
        <textarea
          v-model="description"
          @blur="validate('description')"
          ref="inputDescription"
          class="textarea"
          :class="{ 'is-danger': checkEmpty(errors.description) === false }"
          :placeholder="$t('shortenUrl.form.descriptionPlaceholder')"
        ></textarea>
      </div>
      <p
        v-if="checkEmpty(errors.description) === false"
        class="help is-danger"
      >
        {{ errors.description[0] }}
      </p>
    </div>

    <div class="field mt-6">
      <label class="label">
        {{ $t('form.isViaJumpPageLabel') }}
        <span class="has-text-danger-dark">*</span>
      </label>
      <div class="control">
        <label class="radio">
          <input
            type="radio"
            name="isMeasure"
            v-model="isMeasure"
            :value="true"
          />
          {{ $t('shortenUrl.form.isMeasureLabelYes') }}
        </label>
        <label class="radio ml-4">
          <input
            type="radio"
            name="isMeasure"
            v-model="isMeasure"
            :value="false"
          />
          {{ $t('shortenUrl.form.isMeasureLabelNo') }}
        </label>
      </div>
      <p
        v-if="checkEmpty(errors.isMeasure) === false"
        class="help is-danger"
      >
        {{ errors.isMeasure[0] }}
      </p>
    </div>

    <div
      v-if="isMeasure"
      class="field mt-5"
    >
      <div class="control">
        <label class="radio">
          <input
            type="radio"
            name="isUsePresetParams"
            v-model="isUsePresetParams"
            :value="true"
          />
          {{ $t('shortenUrl.form.isUsePresetParamsLabelYes') }}
        </label>
        <label class="radio ml-4">
          <input
            type="radio"
            name="isUsePresetParams"
            v-model="isUsePresetParams"
            :value="false"
          />
          {{ $t('shortenUrl.form.isUsePresetParamsLabelNo') }}
        </label>
      </div>
      <p class="help">{{ $t('shortenUrl.form.isUsePresetParamsHelperText') }}</p>
      <p
        v-if="checkEmpty(errors.isUsePresetParams) === false"
        class="help is-danger"
      >
        {{ errors.isUsePresetParams[0] }}
      </p>
    </div>

    <div
      v-if="isMeasure && isUsePresetParams"
      class="field mt-4"
    >
      <div class="field">
        <label class="label">
          {{ $t('shortenUrl.form.trackingParamMedia') }}
          <InputRequiredSymbol />
        </label>
        <div class="control">
          <div
            class="select"
            :class="{ 'is-danger': checkEmpty(errors.paramValueMedia) === false }"
          >
            <select
              v-model="paramValueMedia"
              @change="validate('paramValueMedia')"
            >
              <option
                v-for="opt in paramValueMediaOptions"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.label }}
              </option>
            </select>
          </div>
        </div>
        <p
          v-if="checkEmpty(errors.paramValueMedia) === false"
          class="help is-danger"
        >
          {{ errors.paramValueMedia[0] }}
        </p>
      </div>
      <div class="field">
        <label class="label">{{ $t('shortenUrl.form.trackingParamLocation') }}</label>
        <div class="control">
          <div
            class="select"
            :class="{ 'is-danger': checkEmpty(errors.paramValueLocation) === false }"
          >
            <select
              v-model="paramValueLocation"
              @change="validate('paramValueLocation')"
            >
              <option
                v-for="opt in paramValueLocationOptions"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.label }}
              </option>
            </select>
          </div>
        </div>
        <p
          v-if="checkEmpty(errors.paramValueLocation) === false"
          class="help is-danger"
        >
          {{ errors.paramValueLocation[0] }}
        </p>
      </div>

      <div class="field">
        <label class="label">{{ $t('shortenUrl.form.trackingParamOptionalSuffix') }}</label>
        <div class="control">
          <input
            type="text"
            v-model="paramValueOptionalSuffix"
            @blur="validate('paramValueOptionalSuffix')"
            class="input max-w-100px"
            :class="{ 'is-danger': checkEmpty(errors.paramValueOptionalSuffix) === false }"
          />
        </div>
        <p
          v-if="checkEmpty(errors.paramValueOptionalSuffix) === false"
          class="help is-danger"
        >
          {{ errors.paramValueOptionalSuffix[0] }}
        </p>
      </div>

      <div
        class="field"
        v-if="generateTrackingParamValue"
      >
        <label class="label">{{ $t('shortenUrl.form.generateTrackingParamValue') }}</label>
        <div
          class="control pt-2"
          has-background-light
        >
          <span class="has-background-light has-text-weight-semibold px-4 py-2 is-size-6">
            {{ generateTrackingParamValue }}
          </span>
        </div>
      </div>
    </div>
    <div
      v-if="isMeasure && !isUsePresetParams && !isInitialLoading"
      class="field mt-4"
    >
      <!-- <label class="label">{{
        $t('common.paramsFor', { target: $t('term.accessAnalysis') })
      }}</label> -->
      <div class="field-body">
        <div class="field is-grouped is-flex">
          <div
            v-if="isEditableParamKey"
            class="field is-flex-grow-1 is-flex-shrink-1 pr-1"
          >
            <label class="label">paramKey</label>
            <div class="control is-clearfix">
              <input
                type="text"
                v-model="paramKey"
                @blur="validate('paramKey')"
                class="input"
                :class="{ 'is-danger': checkEmpty(errors.paramKey) === false }"
              />
            </div>
            <p
              v-if="checkEmpty(errors.paramKey) === false"
              class="help is-danger"
            >
              {{ errors.paramKey[0] }}
            </p>
          </div>
          <div class="field is-flex-grow-1 is-flex-shrink-1 pl-1">
            <label class="label">{{ $t('shortenUrl.form.paramValue') }}</label>
            <div class="control is-clearfix">
              <input
                type="text"
                v-model="paramValue"
                @blur="validate('paramValue')"
                class="input max-w-300px"
                :class="{ 'is-danger': checkEmpty(errors.paramValue) === false }"
              />
            </div>
            <p
              v-if="checkEmpty(errors.paramValue) === false"
              class="help is-danger"
            >
              {{ errors.paramValue[0] }}
            </p>
            <p class="help">
              {{ $t('shortenUrl.form.paramValueHelperText') }}
            </p>
          </div>
        </div>
      </div>
      <p
        v-if="checkEmpty(paramKeyValueErrors) === false"
        class="help is-danger"
      >
        {{ paramKeyValueErrors[0] }}
      </p>
    </div>

    <div
      v-if="isSetJumpPageConfigs && !isForceViaJumpPage"
      class="field mt-6"
    >
      <label class="label">
        {{ $t('form.isViaJumpPageLabel') }}
      </label>
      <div class="flex align-items-center">
        <label class="checkbox">
          <input
            v-model="isViaJumpPage"
            :value="true"
            type="checkbox"
          />
          {{ $t('shortenUrl.form.isViaJumpPageLabel') }}
        </label>
        <div
          v-if="$t('shortenUrl.form.isViaJumpPageLabelSub')"
          class="ml-4"
        >
          {{ $t('shortenUrl.form.isViaJumpPageLabelSub') }}
        </div>
      </div>
      <p
        v-if="checkEmpty(errors.isViaJumpPage) === false"
        class="help is-danger"
      >
        {{ errors.isViaJumpPage[0] }}
      </p>
    </div>

    <div
      v-if="generatedUrl"
      class="p-3 mt-6 has-background-light u-wrap"
    >
      <h5 class="title is-6">{{ $t('term.generateUrl') }}</h5>
      <div>
        <a
          :href="generatedUrl"
          target="_blank"
          >{{ generatedUrl }}</a
        >
      </div>

      <div
        v-if="isEdit"
        class="field mt-6"
        id="assigneeSection"
      >
        <!-- <label class="label"></label> -->
        <div class="flex align-items-center">
          <label class="checkbox">
            <input
              v-model="isConfirmed"
              :value="true"
              type="checkbox"
            />
            {{ $t('common.confirmed') }}
          </label>
        </div>
        <p
          v-if="checkEmpty(errors.isConfirmed) === false"
          class="help is-danger"
        >
          {{ errors.isConfirmed[0] }}
        </p>
      </div>

      <div
        v-if="isEdit"
        class="field mt-5"
      >
        <label class="label">{{ $t('shortenUrl.form.assigneeName') }}</label>
        <div class="control">
          <input
            type="text"
            v-model="assigneeName"
            @blur="validate('assigneeName')"
            class="input"
            :class="{ 'is-danger': checkEmpty(errors.assigneeName) === false }"
          />
        </div>
        <p
          v-if="checkEmpty(errors.assigneeName) === false"
          class="help is-danger"
        >
          {{ errors.assigneeName[0] }}
        </p>
        <p class="help">
          {{ $t('shortenUrl.msg.assigneeNameIsRequiredOnCheckedIsConfirmed') }}
        </p>
      </div>

      <div
        v-if="isEdit"
        class="field mt-5"
      >
        <label class="label">{{ $t('common.memo') }}</label>
        <div class="control">
          <textarea
            v-model="assigneeMemo"
            @blur="validate('assigneeMemo')"
            class="textarea"
            :class="{ 'is-danger': checkEmpty(errors.assigneeMemo) === false }"
            :placeholder="$t('shortenUrl.form.assigneeMemoPlaceholder')"
          ></textarea>
        </div>
        <p
          v-if="checkEmpty(errors.assigneeMemo) === false"
          class="help is-danger"
        >
          {{ errors.assigneeMemo[0] }}
        </p>
      </div>
    </div>

    <div
      v-if="globalError"
      class="block has-text-danger mt-5"
    >
      {{ globalError }}
    </div>

    <div class="field mt-6">
      <div class="control">
        <button
          class="button is-info"
          @click="save(false)"
        >
          {{ $t('common.save') }}
        </button>
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
import axios from 'axios'
import common from '@/util/common'
import str from '@/util/str'
import { Admin } from '@/api'
// import trackingParams from '@/config/trackingParameters'
import { siteMixin } from '@/mixins/site'
import InputRequiredSymbol from '@/components/atoms/InputRequiredSymbol'

export default {
  mixins: [siteMixin],

  components: {
    InputRequiredSymbol
  },

  props: {
    shortenUrl: {
      type: Object,
      default: null
    }
  },

  data() {
    return {
      name: '',
      description: '',
      url: '',
      paramKey: '',
      isEditableParamKey: false,
      trackingParams: null,
      paramValue: '',
      paramValueMedia: '',
      paramValueLocation: '',
      paramValueOptionalSuffix: '',
      isViaJumpPage: false,
      isForceViaJumpPage: false,
      isMeasure: true,
      isUsePresetParams: false,
      isConfirmed: false,
      assigneeName: '',
      assigneeMemo: '',
      fieldKeys: [
        'name',
        'description',
        'url',
        'isViaJumpPage',
        'paramKey',
        'paramValue',
        'paramValueMedia',
        'paramValueLocation',
        'paramValueOptionalSuffix',
        'isMeasure',
        'isUsePresetParams',
        'isConfirmed',
        'assigneeName',
        'assigneeMemo'
      ],
      errors: [],
      paramKeyValueErrors: [],
      serviceConfigs: null,
      isInitialLoading: false
    }
  },

  computed: {
    serviceId() {
      return this.$route.params.serviceId
    },

    isLoading() {
      return this.$store.state.isLoading
    },

    isEdit() {
      return this.shortenUrl != null
    },

    isEmptyRequiredFields() {
      if (!this.checkEmpty(this.url)) return false
      return true
    },

    parsedUrl() {
      if (this.checkEmpty(this.url) === true) return
      return new URL(this.url)
    },

    isSetJumpPageConfigs() {
      if (!this.serviceConfigs) return false
      if (common.checkObjHasProp(this.serviceConfigs, 'jumpPageUrl') === false) return false
      if (!this.serviceConfigs.jumpPageUrl) return false
      if (!this.serviceConfigs.jumpPageParamKey) return false
      return true
    },

    generatedUrl() {
      if (!this.serviceConfigs) return ''
      if (this.checkEmpty(this.url) === true) return ''
      if (str.checkUrl(this.url) === false) return ''

      let addedQuery = ''
      if (this.isMeasure && this.paramKey && this.paramValue) {
        const prefix = 'qr'
        const suffix = this.isEdit
          ? this.padZero(this.shortenUrl.serviceSeqNumber, 5)
          : this.$t('shortenUrl.form.generatedSeqNo')
        addedQuery = `${this.paramKey}=${prefix}-${this.paramValue}-${suffix}`
      }
      const hash = this.parsedUrl.hash

      let items = []
      if (this.isViaJumpPage) {
        items = [this.parsedUrl.origin, this.parsedUrl.pathname, this.parsedUrl.search, hash]
        const targetUrl = items.join('')

        const parsedUrl = new URL(this.serviceConfigs.jumpPageUrl)
        const delimitter = parsedUrl.search ? '&' : '?'
        items = [
          this.serviceConfigs.jumpPageUrl,
          delimitter,
          this.serviceConfigs.jumpPageParamKey,
          '=',
          encodeURIComponent(targetUrl),
          addedQuery ? '&' : '',
          addedQuery
        ]
      } else {
        let delimitter = ''
        if (addedQuery) {
          delimitter = this.parsedUrl.search ? '&' : '?'
        }
        items = [
          this.parsedUrl.origin,
          this.parsedUrl.pathname,
          this.parsedUrl.search,
          delimitter,
          addedQuery,
          hash
        ]
      }
      return items.join('')
    },

    hasErrors() {
      if (this.globalError) return true

      let hasError = false
      Object.keys(this.errors).map((field) => {
        if (this.errors[field].length > 0) {
          hasError = true
        }
      })
      if (this.paramKeyValueErrors.length > 0) hasError = true
      return hasError
    },

    generateTrackingParamValue() {
      let items = []
      if (this.paramValueMedia) items.push(this.paramValueMedia)
      if (this.paramValueLocation) items.push(this.paramValueLocation)
      if (this.paramValueOptionalSuffix) items.push(this.paramValueOptionalSuffix)
      return items.join('-')
    },

    paramValueMediaOptions() {
      const options = [{ value: '', label: this.$t('msg.pleaseSelect') }]
      if (!this.trackingParams || !this.trackingParams.media) return options
      this.trackingParams.media.map((item) => {
        options.push({ value: item.value, label: item.label })
      })
      return options
    },

    paramsValueMediaValues() {
      if (!this.trackingParams || !this.trackingParams.media) return []
      return this.trackingParams.media.map((item) => item.value)
    },

    paramValueLocationOptions() {
      const options = [{ value: '', label: this.$t('msg.pleaseSelect') }]
      if (!this.trackingParams || !this.trackingParams.locations) return options
      this.trackingParams.locations.map((item) => {
        options.push({ value: item.value, label: item.label })
      })
      return options
    },

    paramsValueLocationValues() {
      if (!this.trackingParams || !this.trackingParams.locations) return []
      return this.trackingParams.locations.map((item) => item.value)
    }
  },

  watch: {
    generateTrackingParamValue(val) {
      this.paramValue = val
    },

    paramValue(val) {
      this.validate('paramValue')
    },

    isMeasure(val) {
      if (val && !this.paramKey) {
        this.paramKey = this.serviceConfigs.analysisParamKeyDefault
      }
    }
  },

  async created() {
    this.isInitialLoading = true
    this.paramKeyValueErrors = []
    await this.setServiceConfigs()
    if (this.isEdit === true) {
      this.setShortenUrl()
    }
    this.setInitValues()

    await this.setTrackingParams()
    if (this.isEdit) {
      this.isUsePresetParams = this.setPresetParamsByParamValue()
    } else if (this.trackingParams != null) {
      this.isUsePresetParams = true
    }
    this.isInitialLoading = false
  },

  methods: {
    setInitValues() {
      if (this.serviceConfigs == null) return
      if (this.serviceConfigs.analysisParamKeyDefault) {
        if (!this.paramKey) this.paramKey = this.serviceConfigs.analysisParamKeyDefault
      }
      if (this.serviceConfigs.jumpPageUrl && this.serviceConfigs.jumpPageParamKey) {
        if (!this.isEdit) this.isViaJumpPage = true
        this.isForceViaJumpPage = true
      }
    },

    setShortenUrl() {
      this.name = this.shortenUrl.name != null ? String(this.shortenUrl.name) : ''
      this.url = this.shortenUrl.url != null ? String(this.shortenUrl.url) : ''
      this.description =
        this.shortenUrl.description != null ? String(this.shortenUrl.description) : ''
      this.isViaJumpPage = this.shortenUrl.isViaJumpPage
      this.paramKey = this.shortenUrl.paramKey != null ? String(this.shortenUrl.paramKey) : ''
      this.paramValue = this.shortenUrl.paramValue != null ? String(this.shortenUrl.paramValue) : ''
      this.isMeasure = Boolean(this.shortenUrl.paramValue)
      this.isConfirmed = this.shortenUrl.confirmStatus === 'confirmed'
      this.assigneeName =
        this.shortenUrl.assigneeName != null ? String(this.shortenUrl.assigneeName) : ''
      this.assigneeMemo =
        this.shortenUrl.assigneeMemo != null ? String(this.shortenUrl.assigneeMemo) : ''
    },

    setPresetParamsByParamValue() {
      if (!this.paramValue) return false
      const regex = /^([A-Za-z0-9_]+)(?:-([A-Za-z0-9_]+))?(?:-(\d+))?$/
      const match = this.paramValue.match(regex)
      if (!match) return false

      const item1 = match[1] || ''
      let item2 = ''
      let item3 = ''

      // 2番目のマッチが数値のみの場合はitem3に、そうでない場合はitem2に割り当てる
      if (match[3] !== undefined) {
        // 直接3番目のグループにマッチしている場合
        item3 = match[3]
        item2 = match[2] || '' // 2番目がundefinedでも空文字列を割り当てる
      } else if (match[2] !== undefined) {
        // 2番目のグループが数値かどうかをチェック
        if (/^\d+$/.test(match[2])) {
          item3 = match[2]
        } else {
          item2 = match[2]
        }
      }
      if (!item1) return false
      if (!this.paramsValueMediaValues.includes(item1)) return false
      this.isUsePresetParams = true
      this.paramValueMedia = item1
      this.paramValueLocation = item2
      this.paramValueOptionalSuffix = item3
      return true
    },

    resetInputs() {
      this.url = ''
      this.name = ''
      this.description = ''
      this.isViaJumpPage = false
      this.paramKey = ''
      this.paramValue = ''
      this.paramValueMedia = ''
      this.paramValueLocation = ''
      this.paramValueOptionalSuffix = ''
      this.isUsePresetParams = false
      this.isMeasure = false
      this.isConfirmed = false
      this.assigneeName = ''
      this.assigneeMemo = ''
    },

    async setServiceConfigs() {
      try {
        this.$store.dispatch('setLoading', true)
        const service = await Admin.getServices(this.serviceId, null, this.adminUserToken)
        if (common.checkObjHasProp(service, 'configs')) {
          this.serviceConfigs = service.configs
        }
      } catch (err) {
        this.debugOutput(err)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      } finally {
        this.$store.dispatch('setLoading', false)
      }
    },

    async setTrackingParams() {
      if (!this.serviceConfigs) return
      if (!this.serviceConfigs.analysisParamsGetApiUrl) return
      const analysisParamsGetApiUrl = this.serviceConfigs.analysisParamsGetApiUrl
      try {
        // this.$store.dispatch('setLoading', true)
        const res = await axios.get(analysisParamsGetApiUrl)
        if (!res.data.bodyJson) {
          throw new Error('Failed to get tracking parameters')
        }
        this.trackingParams = res.data.bodyJson
      } catch (err) {
        this.debugOutput(err)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      } finally {
        // this.$store.dispatch('setLoading', false)
      }
    },

    async save() {
      this.validateAll()
      if (this.hasErrors) return

      try {
        this.$store.dispatch('setLoading', true)
        let vals = {}
        vals.url = this.url
        vals.name = this.name
        vals.description = this.description
        vals.isViaJumpPage = this.isViaJumpPage
        if (this.isMeasure) {
          vals.paramKey = this.paramKey
          vals.paramValue = this.paramValue
        } else {
          vals.paramKey = ''
          vals.paramValue = ''
        }
        vals.isConfirmed = this.isConfirmed
        vals.assigneeName = this.assigneeName
        vals.assigneeMemo = this.assigneeMemo
        let res
        if (this.isEdit) {
          res = await Admin.updateShortenUrl(
            this.serviceId,
            this.shortenUrl.urlId,
            vals,
            this.adminUserToken
          )
        } else {
          res = await Admin.createShortenUrl(this.serviceId, vals, this.adminUserToken)
          this.$store.dispatch('resetAdminShortenUrlsPager', false)
        }
        //this.$emit('posted', res)
        this.$router.push(`/admin/shorten-urls/${this.serviceId}/${res.urlId}`)
        this.resetInputs()
      } catch (err) {
        this.debugOutput(err)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        const msgKey = this.isEdit ? 'Edit failed' : 'Create failed'
        this.handleApiError(err, this.$t(`msg["${msgKey}"]`))
      } finally {
        this.$store.dispatch('setLoading', false)
      }
    },

    cancel() {
      this.resetInputs()
      this.$router.push(`/admin/shorten-urls/${this.serviceId}`)
    },

    validateAll() {
      this.fieldKeys.map((field) => {
        this.validate(field)
      })
      if (this.isMeasure) {
        // if (this.paramKey && !this.paramValue) {
        //   this.paramKeyValueErrors.push(this.$t('msg.inputRequiredBoth'))
        // } else if (!this.paramKey && this.paramValue) {
        //   this.paramKeyValueErrors.push(this.$t('msg.inputRequiredBoth'))
        // }
      }
      // if ((this.paramKey && !this.paramValue) || (!this.paramKey && this.paramValue)) {
      //   this.paramKeyValueErrors.push(this.$t('msg.inputRequiredBoth'))
      // }
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

    validateName() {
      this.initError('name')
      if (this.name === null) this.name = ''
      this.name = this.name.trim()
    },

    validateUrl() {
      this.initError('url')
      if (this.url === null) this.url = ''
      this.url = this.url.trim()
      if (this.checkEmpty(this.url)) this.errors.url.push(this.$t('msg["Input required"]'))
      if (str.checkUrl(this.url) === false) this.errors.url.push(this.$t('msg.InvalidInput'))
    },

    validateDescription() {
      this.initError('description')
      if (this.description === null) this.description = ''
      this.description = this.description.trimEnd()
    },

    validateIsViaJumpPage() {
      this.initError('isViaJumpPage')
    },

    validateParamKey() {
      this.initError('paramKey')
      this.paramKeyValueErrors = []
      if (this.paramKey === null) this.paramKey = ''
      this.paramKey = this.paramKey.trim()
      if (this.paramKey && str.checkKeyString(this.paramKey) === false) {
        this.errors.paramKey.push(this.$t('msg.InvalidInput'))
      }
    },

    validateIsMeasure() {
      this.initError('isMeasure')
    },

    validateIsUsePresetParams() {
      this.initError('isUsePresetParams')
    },

    validateIsConfirmed() {
      this.initError('isConfirmed')
    },

    validateParamValue() {
      this.initError('paramValue')
      this.paramKeyValueErrors = []
      if (this.paramValue === null) this.paramValue = ''
      this.paramValue = this.paramValue.trim()
      if (!this.isMeasure) return
      if (!this.paramValue) {
        this.errors.paramValue.push(this.$t('msg["Input required"]'))
      }
      // if (!this.isUsePresetParams && !this.checkEnabledStrForParam(this.paramValue)) {
      //   this.errors.paramValue.push(this.$t('msg.enableToInputAlphanumericUnderscore'))
      // }
    },

    validateParamValueMedia() {
      this.initError('paramValueMedia')
      if (!this.isMeasure) return
      if (!this.isUsePresetParams) return
      if (!this.paramValueMedia) {
        this.errors.paramValueMedia.push(this.$t('msg.selectRequired'))
      }
      if (!this.paramsValueMediaValues.includes(this.paramValueMedia)) {
        this.errors.paramValueMedia.push(this.$t('msg.InvalidInput'))
      }
    },

    validateParamValueLocation() {
      this.initError('paramValueLocation')
      if (!this.isMeasure) return
      if (!this.paramValueLocation) return
      if (!this.paramsValueLocationValues.includes(this.paramValueLocation)) {
        this.errors.paramValueLocation.push(this.$t('msg.InvalidInput'))
      }
    },

    validateParamValueOptionalSuffix() {
      this.initError('paramValueOptionalSuffix')
      if (!this.isMeasure) return
      if (!this.isUsePresetParams) return
      if (this.paramOptionalValueSuffix === null) this.paramValueOptionalSuffix = ''
      this.paramValueOptionalSuffix = this.paramValueOptionalSuffix.trim()
      if (this.paramValueOptionalSuffix && /^\d+$/.test(this.paramValueOptionalSuffix) === false) {
        this.errors.paramValueOptionalSuffix.push(this.$t('msg.InvalidInput'))
      }
    },

    validateAssigneeName() {
      this.initError('assigneeName')
      if (this.assigneeName === null) this.assigneeName = ''
      this.assigneeName = this.assigneeName.trim()
      if (this.isConfirmed && !this.assigneeName) {
        this.errors.assigneeName.push(this.$t('msg["Input required"]'))
      }
    },

    validateAssigneeMemo() {
      this.initError('assigneeMemo')
      if (this.assigneeMemo === null) this.assigneeMemo = ''
      this.assigneeMemo = this.assigneeMemo.trimEnd()
    },

    checkEnabledStrForParam(str) {
      return /^[A-Za-z0-9_]+$/.test(str)
    }
  }
}
</script>

<template>
  <div v-if="shortenUrl">
    <div class="block">
      <router-link :to="listPageUriObj">
        <i class="fas fa-chevron-left"></i>
        <span>{{ $t('page.ShortenUrlList') }}</span>
      </router-link>
    </div>

    <h1 class="title mt-6">No: {{ serviceSeqNumStr }}</h1>
    <h2 class="subtitle is-6 has-text-grey-light has-text-weight-semibold">
      {{ shortenUrl.urlId }}
    </h2>

    <div>
      <PsAssigneeConfirmStatus :is-confirmed="isConfirmed" />
      <div class="is-pulled-right">
        <eb-dropdown
          v-if="hasEditorRole"
          position="is-right"
        >
          <template v-slot:label>
            <span class="icon">
              <i class="fas fa-edit"></i>
            </span>
          </template>
          <div class="dropdown-content">
            <router-link
              :to="`/admin/shorten-urls/${serviceId}/${shortenUrl.urlId}/edit`"
              class="dropdown-item"
            >
              <span class="icon">
                <i class="fas fa-pen"></i>
              </span>
              <span>{{ $t('common.edit') }}</span>
            </router-link>

            <a
              @click="isConfirmDeleteDialogActive = true"
              class="dropdown-item is-clickable"
            >
              <span class="icon">
                <i class="fas fa-trash"></i>
              </span>
              <span>{{ $t('common.delete') }}</span>
            </a>
          </div>
        </eb-dropdown>

        <EbDialog
          v-model="isConfirmDeleteDialogActive"
          :header-label="$t('common.confirmTo', { action: $t('common.delete') })"
          :execute-button-label="$t('common.delete')"
          execute-button-type="is-danger"
          @execute="deleteShortenUrl()"
          @close="isConfirmDeleteDialogActive = false"
        >
          <p>{{ $t('msg.cofirmToDelete') }}</p>
        </EbDialog>
      </div>
    </div>

    <div class="field mt-5">
      <label class="label">{{ $t('common.memo') }}</label>
      <div
        class="control"
        v-html="usableTextEscaped(shortenUrl.description)"
      ></div>
    </div>

    <div class="mt-6">
      <div class="field">
        <label class="label">{{ $t('common.locationTo') }}</label>
        <div class="control">
          <a
            :href="shortenUrl.url"
            target="_blank"
            >{{ shortenUrl.url }}</a
          >
        </div>
      </div>

      <div class="field mt-5">
        <label class="label">{{ $t('shortenUrl.form.isMeasureLabelYesShort') }}</label>
        <div
          v-text="
            shortenUrl.paramKey && shortenUrl.paramValue ? $t('common.set') : $t('common.notSet')
          "
          class="control"
        ></div>
      </div>

      <div class="field">
        <label class="label">{{
          $t('common.paramsFor', { target: $t('term.accessAnalysis') })
        }}</label>
        <div
          v-if="shortenUrl.paramValue"
          v-text="`${shortenUrl.paramKey}=${shortenUrl.paramValue}`"
          class="control"
        ></div>
        <div
          v-else
          class="control"
        >
          {{ $t('common.notSet') }}
        </div>
      </div>

      <div class="field mt-5">
        <label class="label">{{ $t('shortenUrl.form.isViaJumpPageLabelShort') }}</label>
        <div
          v-text="shortenUrl.isViaJumpPage ? $t('common.set') : $t('common.notSet')"
          class="control"
        ></div>
      </div>
    </div>

    <div
      v-if="isConfirmed"
      class="mt-6 p-4 has-background-light"
    >
      <div class="field mt-5">
        <label class="label">{{ $t('term.generatedUrl') }}</label>
        <div class="control u-wrap">
          <a
            :href="shortenUrl.locationTo"
            target="_blank"
            >{{ shortenUrl.locationTo }}</a
          >
        </div>
      </div>

      <div class="field mt-5">
        <label class="label">{{ $t('term.shortenUrl') }}</label>
        <div class="control">
          <a
            :href="redirectUrl"
            class="is-size-5"
            target="_blank"
            >{{ redirectUrl }}</a
          >
        </div>
      </div>
      <div
        v-if="isDispQrCode"
        class="mt-3"
      >
        <div><img :src="qrCodeUrl" /></div>
        <div class="mt-2">
          <a
            :href="qrCodeUrl"
            :download="`${urlId}.png`"
            target="_blank"
            >{{ $t('common.download') }}</a
          >
        </div>
      </div>
      <div
        class="mt-3 has-text-warning-dark"
        v-else-if="isLoading === false"
      >
        {{ $t('msg.generateItemRequiresTimes', { target: $t('common.images') }) }}
      </div>
    </div>

    <hr />

    <dl class="horizontal-list">
      <div>
        <dt>{{ $t('common.status') }}</dt>
        <dd>
          <PsAssigneeConfirmStatus :is-confirmed="isConfirmed" />
          <RouterLink
            v-if="!isConfirmed && hasEditorRole"
            :to="`/admin/shorten-urls/${serviceId}/${urlId}/edit#assigneeSection`"
            class="ml-4"
          >
            {{ $t('common.doUpdate') }}
          </RouterLink>
        </dd>
      </div>
      <div>
        <dt>{{ $t('common.create') }}</dt>
        <dd>
          <span>
            <inline-time :datetime="shortenUrl.createdAt"></inline-time>
          </span>
          <span class="ml-4 has-text-weight-semibold">
            {{ shortenUrl.createdBy }}
          </span>
        </dd>
      </div>
      <div>
        <dt v-if="isConfirmed">
          {{ $t('common.confirmation') }}
        </dt>
        <dd v-if="isConfirmed">
          <span>
            <inline-time :datetime="shortenUrl.confirmedAt"></inline-time>
          </span>
          <span class="ml-4 has-text-weight-semibold">
            {{ shortenUrl.assigneeName }}
          </span>
        </dd>
      </div>
      <div>
        <dt v-if="shortenUrl.assigneeMemo">
          {{ $t('common.memo') }}
        </dt>
        <dd
          v-if="shortenUrl.assigneeMemo"
          v-html="usableTextEscaped(shortenUrl.assigneeMemo)"
        ></dd>
      </div>
    </dl>
  </div>
</template>
<script>
import config from '@/config/config'
import utilDate from '@/util/date'
import { Admin } from '@/api'
import { siteMixin } from '@/mixins/site'
import EbDropdown from '@/components/molecules/EbDropdown'
import EbDialog from '@/components/molecules/EbDialog'
import PsAssigneeConfirmStatus from '@/components/atoms/PsAssigneeConfirmStatus'
import InlineTime from '@/components/atoms/InlineTime'

export default {
  mixins: [siteMixin],

  components: {
    EbDropdown,
    EbDialog,
    InlineTime,
    PsAssigneeConfirmStatus
  },

  data() {
    return {
      shortenUrl: null,
      isDispQrCode: false,
      isConfirmDeleteDialogActive: false
    }
  },

  computed: {
    serviceId() {
      return this.$route.params.serviceId
    },

    urlId() {
      return this.$route.params.urlId
    },

    isConfirmed() {
      return this.shortenUrl.confirmStatus === 'confirmed'
    },

    serviceSeqNumStr() {
      return this.padZero(this.shortenUrl.serviceSeqNumber)
    },

    qrCodeFileName() {
      const items = ['qr', this.shortenUrl.urlId, this.serviceSeqNumStr]
      return items.join('-') + '.png'
    },

    qrCodeUrl() {
      return `${config.media.url}/shorten-url/qrcodes/${this.qrCodeFileName}`
    },

    redirectUrl() {
      return `${config.shortenUrl.redirectBaseUrl}${this.urlId}`
    },

    listPageUriObj() {
      const path = `/admin/shorten-urls/${this.serviceId}`
      const query = this.$store.getters.adminShortenUrlsPagerQueryCurrent()
      return { path: path, query: query }
    }
  },

  async created() {
    await this.getShortenUrl()
    this.displayQrCode()
  },

  methods: {
    async getShortenUrl() {
      this.shortenUrl = await Admin.getShortenUrls(
        this.serviceId,
        this.urlId,
        null,
        this.adminUserToken
      )
    },

    async deleteShortenUrl() {
      try {
        this.$store.dispatch('setLoading', true)
        const res = await Admin.deleteShortenUrl(this.serviceId, this.urlId, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        this.$router.push(`/admin/shorten-urls/${this.serviceId}`)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        this.handleApiError(err, this.$t(`msg["Delete failed"]`))
      }
    },

    displayQrCode() {
      const now = utilDate.nowUtime()
      const createdAt = utilDate.unixtimeFromStr(this.shortenUrl.createdAt)
      if (now - createdAt > config.shortenUrl.waitingTimeForQrCodeCreated) {
        this.isDispQrCode = true
        return
      }
      setTimeout(() => {
        this.isDispQrCode = true
      }, config.shortenUrl.waitingTimeForQrCodeCreated * 1000)
    }
  }
}
</script>

<style lang="css" scoped>
.horizontal-list div {
  display: flex;
  margin-bottom: 1rem;
}

.horizontal-list dt {
  width: 100px;
  min-width: 100px;
  font-weight: bold;
}

.horizontal-list dd {
  flex-grow: 1;
}
</style>

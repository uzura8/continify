<template>
  <div>
    <admin-shorten-urls-filter-form
      :url="reqUrl"
      :confirm-status="reqConfirmStatus"
      @set-url="setFilterUrl"
      @set-confirm-status="setFilterConfirmStatus"
    ></admin-shorten-urls-filter-form>
    <div class="mt-6">
      <div
        v-if="shortenUrls.length > 0"
        class="table-container"
      >
        <table class="table is-hoverable is-fullwidth">
          <thead>
            <tr>
              <th class="is-size-6">No</th>
              <th class="is-size-6">{{ $t('common.url') }}</th>
              <th class="is-size-7 min-w-100px has-text-centered">
                {{ $t('shortenUrl.term.confirmationStatus') }}
              </th>
              <!-- <th class="is-size-7 min-w-50px has-text-centered">
                {{ $t('common.edit') }}
              </th> -->
              <th class="is-size-7">{{ $t('common.createdAt') }}</th>
            </tr>
          </thead>
          <tfoot>
            <tr>
              <th class="is-size-6">No</th>
              <th class="is-size-6">{{ $t('common.url') }}</th>
              <th class="is-size-7 min-w-100px has-text-centered">
                {{ $t('shortenUrl.term.confirmationStatus') }}
              </th>
              <!-- <th class="is-size-7 min-w-50px has-text-centered">
                {{ $t('common.edit') }}
              </th> -->
              <th class="is-size-7">{{ $t('common.createdAt') }}</th>
            </tr>
          </tfoot>
          <tbody>
            <admin-shorten-urls-table-row
              v-for="shortenUrl in shortenUrls"
              :key="shortenUrl.urlId"
              :shorten-url="shortenUrl"
            ></admin-shorten-urls-table-row>
          </tbody>
        </table>
      </div>
      <div
        v-else-if="isLoading === false"
        class="mb-5"
      >
        <p>{{ $t('msg["Data is empty"]') }}</p>
      </div>

      <nav
        class="pagination"
        role="navigation"
        aria-label="pagination"
      >
        <a
          @click="linkToNeighboringPage(true)"
          class="pagination-previous"
          :class="{ 'is-disabled': !existsPrev, 'u-clickable': existsPrev }"
        >
          <span class="icon">
            <i class="fas fa-angle-left"></i>
          </span>
          <span>{{ $t('common.toPrev') }}</span>
        </a>

        <a
          @click="linkToNeighboringPage(false)"
          class="pagination-next"
          :class="{ 'is-disabled': !existsNext, 'u-clickable': existsNext }"
        >
          <span class="icon">
            <i class="fas fa-angle-right"></i>
          </span>
          <span>{{ $t('common.toNext') }}</span>
        </a>

        <ul class="pagination-list">
          <li>
            <router-link
              :to="getRouterObjByPageIndex()"
              class="pagination-link"
              :class="{ 'is-disabled': !existsPrev }"
            >
              <span class="icon">
                <i class="fas fa-angle-double-left"></i>
              </span>
              <span>{{ $t('common.toFirst') }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>
<script>
import { Admin } from '@/api'
import AdminShortenUrlsFilterForm from '@/components/organisms/AdminShortenUrlsFilterForm'
import AdminShortenUrlsTableRow from '@/components/organisms/AdminShortenUrlsTableRow'
import { siteMixin } from '@/mixins/site'
import util from '@/util'

export default {
  mixins: [siteMixin],

  components: {
    AdminShortenUrlsFilterForm,
    AdminShortenUrlsTableRow
  },

  props: {},

  data() {
    return {
      shortenUrls: [],
      count: 50
    }
  },

  computed: {
    serviceId() {
      return this.$route.params.serviceId
    },

    index() {
      return this.$route.query.index ? Number(this.$route.query.index) : 0
    },

    currentPagerKey() {
      const current = this.$store.state.adminShortenUrlsPager.keys.find(
        (item) => item.index === this.index
      )
      return current ? current.key : null
    },

    existsNext() {
      const nextPage = this.index + 1
      return Boolean(
        this.$store.state.adminShortenUrlsPager.keys.find((item) => item.index === nextPage)
      )
    },

    existsPrev() {
      const prevPage = this.index - 1
      return prevPage >= 0
    },

    reqUrl() {
      if (!this.$route.query.url) return ''
      if (!util.str.checkStartWithHttpScheme(this.$route.query.url)) return ''
      return this.$route.query.url
    },

    reqConfirmStatus() {
      if (!this.$route.query.status) return ''
      if (!['confirmed', 'unconfirmed'].includes(this.$route.query.status)) return ''
      return this.$route.query.status
    },

    currentQueryParams() {
      return {
        count: this.count,
        url: this.reqUrl,
        status: this.reqConfirmStatus
      }
    }
  },

  watch: {
    '$route.query': {
      handler(newQuery, oldQuery) {
        this.shortenUrls = []
        this.fetchShortenUrls()
      },
      deep: true // オブジェクト内の変更も監視する
      // immediate: true // コンポーネントのマウント時にもハンドラを実行する
    }
  },

  async created() {
    await this.fetchShortenUrls()
  },

  methods: {
    getRouterObjByPageIndex(index = 0) {
      const params = { ...this.currentQueryParams }
      params.index = String(index)
      return {
        path: `/admin/shorten-urls/${this.serviceId}`,
        query: params
      }
    },

    async fetchShortenUrls() {
      try {
        if (this.index > this.$store.getters.adminShortenUrlsPagerIndexCount() || this.index < 0) {
          this.$store.dispatch('resetAdminShortenUrlsPager', true)
          const routerObj = this.getRouterObjByPageIndex()
          this.$router.replace(routerObj)
          return
        }
        this.$store.dispatch('setLoading', true)
        const params = { ...this.currentQueryParams }
        if (this.currentPagerKey) {
          params.pagerKey = JSON.stringify(this.currentPagerKey)
        }
        const res = await Admin.getShortenUrls(this.serviceId, null, params, this.adminUserToken)
        this.shortenUrls = res.items
        this.$store.dispatch('setAdminShortenUrlsPagerLastIndex', this.index)
        if (res.pagerKey) {
          const item = { index: this.index + 1, key: res.pagerKey }
          this.$store.dispatch('pushItemToAdminShortenUrlsPagerKeys', item)
        }
        // For store
        const paramsForStore = { ...this.currentQueryParams }
        paramsForStore.index = this.index
        await this.$store.dispatch('setAdminShortenUrlsPagerParams', paramsForStore)
        // console.log(44441111, this.$store.state.adminShortenUrlsPager.keys)
      } catch (err) {
        this.debugOutput(err)
        this.handleApiError(err, 'Failed to get data from server')
      } finally {
        this.$store.dispatch('setLoading', false)
      }
    },

    setFilterUrl(url) {
      this.$store.dispatch('resetAdminShortenUrlsPager', true)
      this.$router.push({ query: { url: url } })
    },

    setFilterConfirmStatus(status) {
      this.$store.dispatch('resetAdminShortenUrlsPager', true)
      if (status === 'unconfirmed') {
        this.$router.push({ query: { status: status } })
      } else {
        this.$router.push({ query: null })
      }
    },

    linkToNeighboringPage(isPrev = false) {
      let routerObj
      if (isPrev) {
        if (!this.existsPrev) return
        routerObj = this.getRouterObjByPageIndex(this.index - 1)
      } else {
        if (!this.existsNext) return
        routerObj = this.getRouterObjByPageIndex(this.index + 1)
      }
      this.$router.push(routerObj)
    }
  }
}
</script>

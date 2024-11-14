import 'animate.css'
import store from '@/store'
import router from '@/router'
//import listener from '@/listener'
import util from '@/util'
import config from '@/config/config'
import Cognito from '@/cognito'

const cognito = new Cognito()

export const siteMixin = {
  data() {
    return {
      globalError: '',
      errors: {}
    }
  },

  computed: {
    isLoading() {
      return this.$store.getters.isLoading()
    },

    isAdminPath() {
      return this.$route.path.startsWith('/admin')
    },

    isAdminUser() {
      return this.$store.getters.isAdminUser()
    },

    hasAdminRole() {
      return this.$store.getters.hasAdminRole()
    },

    checkAdminRole(role) {
      return this.$store.getters.checkAdminRole(role)
    },

    hasEditorRole() {
      return this.$store.getters.hasEditorRole()
    },

    adminRole() {
      return this.$store.getters.adminRole()
    },

    //adminUserAcceptServiceIds() {
    //  return this.$store.getters.adminUserAcceptServiceIds()
    //},

    adminUserToken() {
      return this.$store.state.adminUser.token
    },

    adminUserName() {
      return this.$store.state.adminUser ? this.$store.state.adminUser.username : ''
    },

    isAuth: function () {
      return false
    },

    serviceId() {
      return this.$route.params.serviceId
    }
  },

  methods: {
    siteUri: util.site.uri,
    debugOutput: util.site.debugOutput,
    checkEmpty: util.obj.isEmpty,
    checkObjHasProp: util.obj.checkObjHasProp,
    inArray: util.arr.inArray,
    //listenComponent: listener.listen,
    //destroyedComponent: listener.destroyed,
    checkResponseHasErrorMessage: util.site.checkResponseHasErrorMessage,
    showGlobalMessage: util.site.showGlobalMessage,

    mediaUrl: function (type, fileId, mimeType, size = 'raw') {
      const ext = util.media.getExtensionByMimetype(mimeType)
      let pathItems = [config.media.url, this.serviceId]
      if (type === 'image') {
        const fileName = `${size}.${ext}`
        pathItems.push('images', fileId, fileName)
      } else {
        const fileName = `${fileId}.${ext}`
        pathItems.push('docs', fileName)
      }
      return pathItems.join('/')
    },

    handleApiError: function (err, defaultMsg = '', isRedirect = false) {
      if (isRedirect && err != null && err.response != null) {
        if (err.response.status == 401) {
          store.dispatch('resetAuth')
          this.$router.push({
            path: '/signin',
            query: { redirect: this.$route.fullPath }
          })
          return
        } else if (err.response.status == 403) {
          this.$router.push('/error/forbidden')
          return
        } else if (err.response.status == 404) {
          this.$router.push('/error/notfound')
          return
        }
      }
      if (
        typeof this.setErrors == 'function' &&
        util.site.checkResponseHasErrorMessage(err, true)
      ) {
        this.setErrors(err.response.data.errors)
      }
      if (util.site.checkResponseHasErrorMessage(err)) {
        let defaultMessage = ''
        if (err.response.status == 400) {
          defaultMessage = this.$t('msg.InvalidInput')
        } else {
          defaultMessage = this.$t("msg['Error occurred']")
        }
        const fullMessageKey = `msg.${err.response.data.message}`
        const msg = this.$te(fullMessageKey) ? this.$t(fullMessageKey) : defaultMessage

        util.site.showGlobalMessage(msg)
      } else if (defaultMsg) {
        util.site.showGlobalMessage(defaultMsg)
      } else {
        util.site.showGlobalMessage(this.$t('msg["Server error"]'))
      }
    },

    //usableTextSanitized: function (text) {
    //  let conved = util.str.nl2br(text)
    //  conved = util.str.url2link(conved)
    //  return this.$sanitize(conved)
    //},

    usableTextEscaped: function (text) {
      let conved = util.str.escapeHtml(text)
      conved = util.str.nl2br(conved)
      return util.str.url2link(conved)
    },

    convUserTypeToi18n: function (user) {
      if (user.isAdmin) return this.$t('common.admin')
      if (user.isAnonymous) return this.$t('common.anonymous')

      return this.$t('common.normal')
    },

    setErrors: function (errors) {
      errors.map((err) => {
        const field = util.str.convSnakeToCamel(err.field)
        this.initError(field)
        let msg = err.message
        if (this.$t(`msg["${err.message}"]`)) {
          msg = this.$t(`msg["${err.message}"]`)
        }
        this.errors[field].push(msg)
      })
    },

    moveToErrorPage: function (code) {
      if (code == 404) {
        router.push({ path: '/notfound' })
      }
    },

    initError: function (field) {
      this.globalError = ''
      this.errors[field] = []
    },

    initErrors: function (fields = []) {
      this.globalError = ''
      if (fields.length > 0) {
        fields.map((field) => {
          this.initError(field)
        })
      } else {
        Object.keys(this.errors).map((field) => {
          this.initError(field)
        })
      }
    },

    checkPostPublished(statusPublishAt) {
      // 閲覧可能な状態のみ true を返す
      if (statusPublishAt.startsWith('unpublish')) return false
      if (statusPublishAt.startsWith('reserve')) return false
      return true
    },

    getPostPublishStatus(statusPublishAt) {
      if (statusPublishAt.startsWith('unpublish')) return 'unpublished'
      if (statusPublishAt.startsWith('publish')) return 'published'
      if (statusPublishAt.startsWith('reserve')) return 'reserved'
      return ''
    },

    getCategoryLabel(slug) {
      const cates = this.$store.state.categoryItems
      if (this.checkEmpty(cates)) return ''
      const cate = cates.find((item) => item.slug === slug)
      return cate != null ? cate.label : ''
    },

    //getTokenExpirationTime(isFormat = false) {
    //  const utime = cognito.getTokenExpirationTime(this.adminUserToken)
    //  if (isFormat === false) return utime

    //  return util.date.localeStrFromUnixtime(utime)
    //},

    async checkAndRefreshTokens() {
      if (cognito.checkTokenExpired(this.adminUserToken) === false) return

      store.dispatch('setLoading', true)
      const res = await this.refreshSession()
      store.dispatch('setLoading', false)
      if (res === false) {
        store.dispatch('setAdminUser', null)
        this.$router.push({
          path: '/signin',
          query: { redirect: this.$route.fullPath }
        })
      }
    },

    async refreshSession() {
      const username = this.adminUserName
      const refreshToken = this.$store.state.adminUser.refreshToken
      if (!username || !refreshToken) return false
      const session = await cognito.refreshSession(username, refreshToken)
      if (!session) return false

      store.dispatch('setAdminUserTokens', {
        idToken: session.getIdToken().getJwtToken(),
        accessToken: session.getAccessToken().getJwtToken(),
        refreshToken: session.getRefreshToken().getToken()
      })
      return true
    },

    dateFormat(utcDateStr, format = '') {
      return util.date.localeStrFromUtcDate(utcDateStr, format)
    },

    formatBytes(num) {
      return util.str.bytesFormat(num)
    },

    numFormat(num) {
      return util.str.numFormat(num)
    },

    padZero(num, length = 5) {
      return util.str.padZero(num, length)
    }
  }
}

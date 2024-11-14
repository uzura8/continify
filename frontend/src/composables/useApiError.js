import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import utilSite from '@/util/site'

export function useApiError() {
  const store = useStore()
  const router = useRouter()
  const route = useRoute()
  const { t } = useI18n()

  const handleApiError = (err, defaultMsg = '', isRedirect = false) => {
    if (isRedirect && err != null && err.response != null) {
      if (err.response.status == 401) {
        store.dispatch('resetAuth')
        router.push({
          path: '/signin',
          query: { redirect: route.fullPath }
        })
        return
      } else if (err.response.status == 403) {
        router.push('/error/forbidden')
        return
      } else if (err.response.status == 404) {
        router.push('/error/notfound')
        return
      }
    }

    // if (typeof this.setErrors == 'function' && utilSite.checkResponseHasErrorMessage(err, true)) {
    //   this.setErrors(err.response.data.errors)
    // }
    if (utilSite.checkResponseHasErrorMessage(err)) {
      let defaultMessage = ''
      if (err.response.status == 400) {
        defaultMessage = t('msg.InvalidInput')
      } else {
        defaultMessage = t("msg['Error occurred']")
      }
      const fullMessageKey = `msg.${err.response.data.message}`
      const msg = t(fullMessageKey) ? t(fullMessageKey) : defaultMessage

      utilSite.showGlobalMessage(msg)
    } else if (defaultMsg) {
      utilSite.showGlobalMessage(defaultMsg)
    } else {
      utilSite.showGlobalMessage(t('msg["Server error"]'))
    }
  }

  return {
    handleApiError
  }
}

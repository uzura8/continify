import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import Cognito from '@/cognito'

const cognito = new Cognito()

export function useAdminAuth() {
  const store = useStore()
  const router = useRouter()
  const route = useRoute()

  const adminUserName = computed(() =>
    store.state.adminUser ? store.state.adminUser.username : ''
  )

  const adminUserToken = computed(() => (store.state.adminUser ? store.state.adminUser.token : ''))

  const refreshToken = computed(() =>
    store.state.adminUser ? store.state.adminUser.refreshToken : ''
  )

  const refreshSession = async () => {
    if (!adminUserName.value || !refreshToken.value) return false
    const session = await cognito.refreshSession(adminUserName.value, refreshToken.value)
    if (!session) return false

    store.dispatch('setAdminUserTokens', {
      idToken: session.getIdToken().getJwtToken(),
      accessToken: session.getAccessToken().getJwtToken(),
      refreshToken: session.getRefreshToken().getToken()
    })
    return true
  }

  const checkAndRefreshTokens = async () => {
    if (cognito.checkTokenExpired(adminUserToken.value) === false) return

    store.dispatch('setLoading', true)
    const res = await refreshSession()
    store.dispatch('setLoading', false)
    if (res === false) {
      store.dispatch('setAdminUser', null)
      router.push({
        path: '/signin',
        query: { redirect: route.fullPath }
      })
    }
  }

  return {
    adminUserName,
    adminUserToken,
    refreshToken,
    refreshSession,
    checkAndRefreshTokens
  }
}

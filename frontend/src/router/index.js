import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import { Admin } from '@/api'
import store from '@/store'
import Cognito from '@/cognito'
import utilSite from '@/util/site'

const cognito = new Cognito()

const scrollBehavior = (to, _from, savedPosition) => {
  if (to.hash) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          el: to.hash,
          behavior: 'smooth'
        })
      }, 2000)
    })
  } else if (savedPosition) {
    return new Promise((resolve) => {
      setTimeout(() => {
        //savedPosition.behavior = 'smooth'
        resolve(savedPosition)
      }, 2000)
    })
  } else {
    return { left: 0, top: 0 }
  }
}

const adminSignOut = (to, from, next) => {
  cognito.signOut()
  next('/admin/signin')
}

routes.push({
  path: '/admin/signout',
  beforeEnter: adminSignOut
})

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior
})

router.beforeEach(async (to, from, next) => {
  const isAdminPath = to.path.startsWith('/admin')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (isAdminPath) {
    let session
    try {
      session = await cognito.isAuthenticated()
    } catch (err) {
      utilSite.debugOutput(err)
      store.dispatch('setAdminUser', null)
    }
    if (!session) {
      if (requiresAuth) {
        const signInPath = '/admin/signin'
        let nextRoute = { path: signInPath }
        if (to.name !== 'AdminTop') {
          nextRoute.query = { redirect: to.fullPath }
        }
        next(nextRoute)
      } else {
        next()
      }
    } else {
      try {
        const token = session.idToken.jwtToken
        const res = await cognito.getAttribute()
        let attrs = {}
        for (let v of res) {
          let key = v.getName().replace(/^custom\:/g, '')
          attrs[key] = v.getValue()
        }
        const user = {
          username: cognito.currentUser.username,
          attributes: attrs,
          token: token,
          accessToken: session.accessToken.jwtToken,
          refreshToken: session.refreshToken.token
        }
        store.dispatch('setAdminUser', user)
        if (to.matched.some((record) => record.meta.requiresRoleAdmin)) {
          if (store.getters.hasAdminRole() === false) {
            next({ path: '/error/forbidden' })
          }
        }
        if (to.matched.some((record) => record.meta.requiresAcceptService)) {
          const services = await Admin.getAccountServices(null, token)
          const service = services.find((item) => item['serviceId'] === to.params.serviceId)
          if (service == null) {
            next({ path: '/error/forbidden' })
          }
        }
      } catch (err) {
        utilSite.debugOutput(err)
        store.dispatch('setAdminUser', null)
        adminSignOut(to, from, next)
      }
      next()
    }
  } else {
    next()
    // User Auth
    //const signInPath = '/signin'
  }
  store.dispatch('setHeaderMenuOpen', false)
})

export default router

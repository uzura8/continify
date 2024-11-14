import { createStore } from 'vuex'
//import createPersistedState from 'vuex-persistedstate'
import actions from './actions'
import getters from './getters'
import mutations from './mutations'

const store = createStore({
  state() {
    return {
      common: {
        loadingItems: [],
        loadingTimerId: null,
        isHeaderMenuOpen: false,
      },
      auth: {
        state: null,
        user: null,
        token: null,// idToken
        accessToken: null,
        refreshToken: null,
      },
      categoryItems: [],
      adminUser: null,
      adminUserAllowedServiceIds: [],
      adminPostList: [],
      adminPostListServiceId: null,
      adminPostsPager: {
        keys: [],
        lastIndex: 0,
        sort: 'createdAt',
        order: 'desc',
        filters: {
          attribute: '',
          compare: '',
          value: '',
        },
        category: '',
      },
      adminShortenUrlsPager: {
        keys: [],
        lastIndex: 0,
        url: '',
        status: '',
      }
    }
  },
  getters,
  actions,
  mutations,
  plugins: [
    //createPersistedState({
    //  key: 'SampleSiteState',
    //  paths: ['auth'],
    //  //storage: window.sessionStorage
    //})
  ],
  strict: process.env.NODE_ENV !== 'production'
})

export default store

import * as types from './mutation-types'
import obj from '@/util/obj'
import config from '@/config/config'

const loadingMaxDuration = obj.getVal(config, 'loadingMaxDuration', 30) * 1000

export default {
  setHeaderMenuOpen: (ctx, isOpen) => {
    ctx.commit(types.SET_COMMON_HEADER_MENU_OPEN, isOpen)
  },

  setLoading: (ctx, payload) => {
    let isLoading = false
    let key = 'item'
    if (obj.isObject(payload) === true) {
      isLoading = payload.status
      key = payload.key
    } else if (typeof payload === 'boolean') {
      isLoading = payload
    } else {
      isLoading = Boolean(payload)
    }
    const loadingItem = {
      status: isLoading,
      key: key
    }
    const isStartLoading = ctx.state.common.loadingItems.length === 0 && isLoading === true
    ctx.commit(types.SET_COMMON_LOADING, loadingItem)
    const isFinishLoading = ctx.state.common.loadingItems.length === 0 && isLoading === false

    if (isStartLoading) {
      if (!ctx.state.common.loadingTimerId) {
        // If not set timer, set timer to delete all loading items
        const timerId = setTimeout(() => {
          ctx.commit(types.RESET_COMMON_LOADING)
          ctx.commit(types.RESET_COMMON_LOADING_TIMER_ID)
        }, loadingMaxDuration)
        ctx.commit(types.SET_COMMON_LOADING_TIMER_ID, timerId)
      }
    } else if (isFinishLoading) {
      // If loading items not exists, clear timer
      ctx.commit(types.RESET_COMMON_LOADING)
      ctx.commit(types.RESET_COMMON_LOADING_TIMER_ID)
    }
  },

  setAdminUser: async (ctx, payload) => {
    ctx.commit(types.SET_ADMIN_USER, payload)
  },

  setAdminUserTokens: async (ctx, payload) => {
    ctx.commit(types.SET_ADMIN_USER_TOKENS, payload)
  },

  setAdminUserAllowedServiceIds: async (ctx, serviceIds) => {
    ctx.commit(types.SET_ADMIN_USER_ALLOWED_SERVICE_IDS, serviceIds)
  },

  setCategoryItems: async (ctx, payload) => {
    ctx.commit(types.SET_CATEGORY_ITEMS, payload)
  },

  setAdminPostList: async (ctx, payload) => {
    ctx.commit(types.SET_ADMIN_POST_LIST, payload)
  },

  pushItemToAdminPostsPagerKeys: async (ctx, payload) => {
    ctx.commit(types.PUSH_ITEM_TO_ADMIN_POSTS_PAGER_KEYS, payload)
  },

  resetAdminPostsPager: async (ctx, isResetKeys = false) => {
    ctx.commit(types.RESET_ADMIN_POSTS_PAGER, isResetKeys)
  },

  setAdminPostsPagerLastIndex: async (ctx, payload) => {
    ctx.commit(types.SET_ADMIN_POSTS_PAGER_LAST_INDEX, payload)
  },

  setAdminPostsPagerParams: async (ctx, payload) => {
    ctx.commit(types.SET_ADMIN_POSTS_PAGER_PARAMS, payload)
  },
}

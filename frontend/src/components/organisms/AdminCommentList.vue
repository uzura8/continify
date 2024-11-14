<script>
import { ref, computed, watch, onBeforeMount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { useApiError } from '@/composables/useApiError'
import { useAdminAuth } from '@/composables/useAdminAuth'
import { Admin } from '@/api'
import utilSite from '@/util/site'
import AdminCommentListItem from '@/components/molecules/AdminCommentListItem.vue'

export default {
  components: {
    AdminCommentListItem
  },

  props: {
    serviceId: {
      type: String,
      required: true
    },
    contentId: {
      type: String,
      required: false,
      default: ''
    },
    publishStatus: {
      type: String,
      required: false,
      default: ''
    }
  },

  setup(props) {
    const store = useStore()
    const { t } = useI18n()
    const { handleApiError } = useApiError()
    const { checkAndRefreshTokens } = useAdminAuth()

    const comments = ref([])
    const pageToken = ref(null)

    const hasNext = computed(() => {
      return !!pageToken.value
    })

    const fetchContentList = async () => {
      await checkAndRefreshTokens()
      try {
        store.dispatch('setLoading', true)
        const params = {
          count: 20,
          order: 'desc'
        }
        if (props.publishStatus) {
          params.publishStatus = props.publishStatus
        }
        if (pageToken.value) {
          params.pageToken = pageToken.value
        }
        let res = null
        if (props.contentId) {
          res = await Admin.getCommentListByContent(
            props.serviceId,
            props.contentId,
            params,
            store.state.adminUser.token,
            props.contentId
          )
        } else {
          res = await Admin.getCommentList(props.serviceId, params, store.state.adminUser.token)
        }
        if (res) {
          if (res.items && res.items.length) {
            res.items.forEach((item) => {
              comments.value.push(item)
            })
          }
          // if (res.meta && res.meta.count) {
          //   contentList.value = res.meta.count
          // }
          pageToken.value = res.pageToken
        }
      } catch (err) {
        console.log(err)
        handleApiError(err, 'Failed to get data from server')
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    const updatePublishStatus = async (ev) => {
      const { commentId, publishStatus } = ev
      await checkAndRefreshTokens()
      try {
        store.dispatch('setLoading', true)
        const item = await Admin.updateCommentStatus(
          props.serviceId,
          commentId,
          publishStatus,
          store.state.adminUser.token
        )
        const idx = comments.value.findIndex((comment) => comment.commentId === commentId)
        comments.value.splice(idx, 1, item)
      } catch (err) {
        console.log(err)
        handleApiError(err, 'Failed to get data from server')
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    const deleteComment = async (commentId) => {
      await checkAndRefreshTokens()
      try {
        store.dispatch('setLoading', true)
        await Admin.deleteComment(props.serviceId, commentId, store.state.adminUser.token)
        const idx = comments.value.findIndex((comment) => comment.commentId === commentId)
        comments.value.splice(idx, 1)
        utilSite.showGlobalMessage(t('msg.deleteComplete'), 'is-success')
      } catch (err) {
        console.log(err)
        handleApiError(err, 'Failed to get data from server')
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    watch(
      () => props.publishStatus,
      async () => {
        comments.value = []
        pageToken.value = null
        await fetchContentList()
      }
    )

    onBeforeMount(async () => {
      await fetchContentList()
    })

    return {
      comments,
      updatePublishStatus,
      hasNext,
      fetchContentList,
      deleteComment
    }
  }
}
</script>

<template>
  <div>
    <section v-if="comments.length > 0">
      <ul>
        <li
          v-for="comment in comments"
          :key="comment.commentId"
          class="mb-5"
        >
          <AdminCommentListItem
            :comment="comment"
            @update-publish-status="updatePublishStatus"
            @delete-comment="deleteComment"
          />
        </li>
      </ul>
      <div
        v-if="hasNext"
        class="card"
      >
        <footer class="card-footer">
          <a
            class="card-footer-item"
            @click="fetchContentList"
          >
            {{ $t('common.more') }}
          </a>
        </footer>
      </div>
    </section>
    <section v-else>
      <p class="my-6">{{ $t('msg["Data is empty"]') }}</p>
    </section>
  </div>
</template>

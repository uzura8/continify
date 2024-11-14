<script>
import { ref, computed, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
// import { useI18n } from 'vue-i18n'
// import { useAdminAuth } from '@/composables/useAdminAuth'
import { useApiError } from '@/composables/useApiError'
import { Admin } from '@/api'
import AdminCommentList from '@/components/organisms/AdminCommentList'
import EbDropdown from '@/components/molecules/EbDropdown'

export default {
  components: {
    AdminCommentList,
    EbDropdown
  },

  setup() {
    const route = useRoute()
    const store = useStore()
    // const { t } = useI18n()
    const { handleApiError } = useApiError()
    // const { checkAndRefreshTokens } = useAdminAuth()

    const serviceId = computed(() => route.params.serviceId)

    const contentList = ref([])
    const setContentList = async () => {
      // await checkAndRefreshTokens()
      try {
        store.dispatch('setLoading', true)
        const res = await Admin.getServiceContentList(
          serviceId.value,
          null,
          store.state.adminUser.token
        )
        contentList.value = res.items || []
      } catch (err) {
        console.log(err)
        handleApiError(err, 'Failed to get data from server')
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    onBeforeMount(() => {
      setContentList()
    })

    return {
      serviceId,
      contentList
    }
  }
}
</script>

<template>
  <div>
    <h1 class="title">{{ $t('comment.page.adminTop') }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>

    <div class="mt-6 is-flex is-align-items-center is-justify-content-space-between">
      <div class="is-flex is-align-items-center is-justify-content-start">
        <div class="mr-3">ContentID:</div>
        <eb-dropdown position="is-left">
          <template #label>
            <span>
              {{ $t('common.all') }}
            </span>
          </template>
          <div class="dropdown-content">
            <RouterLink
              v-for="content in contentList"
              :key="content.contentId"
              :to="`/admin/comments/${serviceId}/content/${content.contentId}`"
              class="dropdown-item"
            >
              <span>{{ content.contentId }}</span>
            </RouterLink>
          </div>
        </eb-dropdown>
      </div>

      <RouterLink
        :to="`/admin/settings/${serviceId}/content`"
        class="is-flex is-size-6"
      >
        {{ $t('page.managementOf', { label: $t('term.contentId') }) }}
      </RouterLink>
    </div>

    <AdminCommentList
      :service-id="serviceId"
      class="mt-6"
    />
  </div>
</template>

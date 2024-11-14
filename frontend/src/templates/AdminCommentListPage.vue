<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminCommentList from '@/components/organisms/AdminCommentList'

export default {
  components: {
    AdminCommentList
  },

  setup() {
    const route = useRoute()
    const serviceId = computed(() => route.params.serviceId)
    const contentId = computed(() => route.params.contentId)
    const publishStatus = computed(() => route.query.publishStatus)

    return {
      serviceId,
      contentId,
      publishStatus
    }
  }
}
</script>

<template>
  <div>
    <div class="block">
      <RouterLink :to="`/admin/comments/${serviceId}`">
        <i class="fas fa-chevron-left"></i>
        <span>{{ $t('comment.page.adminTop') }}</span>
      </RouterLink>
    </div>

    <h1 class="title">{{ $t('comment.page.commentList') }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>

    <div class="mb-5 is-flex is-align-items-center is-justify-content-start">
      <div class="is-size-7 mr-2">ContentID:</div>
      <div class="has-text-weight-semibold">{{ contentId }}</div>
    </div>

    <div class="tabs">
      <ul>
        <li :class="{ 'is-active': !publishStatus }">
          <RouterLink :to="{ query: { publishStatus: '' } }">
            {{ $t('common.all') }}
          </RouterLink>
        </li>
        <li :class="{ 'is-active': publishStatus === 'publish' }">
          <RouterLink :to="{ query: { publishStatus: 'publish' } }">
            {{ $t('common.onlyFor', { label: $t('form.commentDefaultPublishStatus.publish') }) }}
          </RouterLink>
        </li>
        <li :class="{ 'is-active': publishStatus === 'unpublish' }">
          <RouterLink :to="{ query: { publishStatus: 'unpublish' } }">
            {{ $t('common.onlyFor', { label: $t('form.commentDefaultPublishStatus.unpublish') }) }}
          </RouterLink>
        </li>
      </ul>
    </div>

    <AdminCommentList
      :service-id="serviceId"
      :content-id="contentId"
      :publish-status="publishStatus"
      class="mt-6"
    />
  </div>
</template>

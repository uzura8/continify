<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminSettingContent from '@/components/organisms/AdminSettingContent.vue'

export default {
  components: {
    AdminSettingContent
  },

  setup() {
    const route = useRoute()
    const serviceId = computed(() => route.params.serviceId)
    return {
      serviceId
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
    <h1 class="title">{{ $t('page.managementOf', { label: $t('term.contentId') }) }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>
    <div>
      <p class="">{{ $t('comment.msg.contentSettingPageLead01') }}</p>
      <p class="mt-1">{{ $t('comment.msg.contentSettingPageLead02') }}</p>
    </div>
    <AdminSettingContent
      :service-id="serviceId"
      class="mt-6"
    />
  </div>
</template>

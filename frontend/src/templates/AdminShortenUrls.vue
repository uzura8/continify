<template>
<div>
  <div>
    <h1 class="title">{{ $t('page.ShortenUrlList') }}</h1>

    <router-link
      v-if="hasEditorRole"
      :to="`/admin/shorten-urls/${serviceId}/create`"
      class="button"
    >{{ $t('common.createNew') }}</router-link>
  </div>
  <AdminShortenUrlList class="mt-6" />
</div>
</template>
<script>
import AdminShortenUrlList from '@/components/organisms/AdminShortenUrlList'
import { siteMixin } from '@/mixins/site'

export default{
  mixins: [siteMixin],

  components: {
    AdminShortenUrlList,
  },

  computed: {
    serviceId() {
      return this.$route.params.serviceId
    },
  },
}
</script>


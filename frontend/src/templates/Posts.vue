<template>
<div>
  <div>
    <h1 class="title">{{ $t('common.posts') }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>
  </div>
  <post-list class="mt-6"></post-list>
</div>
</template>
<script>
import PostList from '@/components/organisms/PostList'
import { siteMixin } from '@/mixins/site'

export default{
  mixins: [siteMixin],

  components: {
    PostList,
  },

  data() {
    return {
    }
  },

  computed: {
    serviceId() {
      return this.$route.params.serviceId
    },
  },

  created() {
  },

  methods: {
  },
}
</script>


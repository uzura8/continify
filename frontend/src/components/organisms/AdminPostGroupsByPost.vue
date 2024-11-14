<template>
<div>
  <ul v-if="groups.length > 0">
    <li
      v-for="group in groups"
      :key="group.slug"
      class="block"
    >
      <AdminPostGroupByPost
        :group="group"
        :post-id="postId"
        :initial-post-ids="group.postIds == null ? [] : group.postIds"
      />
    </li>
  </ul>

  <div v-else-if="isLoading === false">
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>
</div>
</template>
<script>
import { Admin } from '@/api'
import AdminPostGroupByPost from '@/components/organisms/AdminPostGroupByPost'
import { siteMixin } from '@/mixins/site'

export default{
  mixins: [siteMixin],

  components: {
    AdminPostGroupByPost,
  },

  props: {
    postId: {
      type: String,
      required: true,
    },
  },

  data(){
    return {
      groups: [],
    }
  },

  computed: {
    serviceId() {
      return this.$route.params.serviceId
    },
  },

  watch: {
  },

  async created() {
    await this.fetchGroups()
  },

  methods: {
    resetGroups() {
      this.groups = []
    },

    async fetchGroups() {
      let params = {}
      this.$store.dispatch('setLoading', true)
      try {
        this.groups = await Admin.getPostGroups(this.serviceId, null, null, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    selectPost(post) {
      this.$emit('select', post)
    },
  },
}
</script>


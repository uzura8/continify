<template>
  <tr>
    <td class="is-size-6 w-180">{{ group.slug }}</td>
    <td class="is-size-6">
      <router-link :to="`/admin/posts/${serviceId}/groups/${group.slug}`">{{
        group.label
      }}</router-link>
    </td>
  </tr>
</template>
<script>
import { siteMixin } from '@/mixins/site'

export default {
  mixins: [siteMixin],

  components: {},

  props: {
    group: {
      type: Object,
      default: null
    }
  },

  data() {
    return {}
  },

  computed: {
    slug() {
      return this.group.slug
    },

    serviceId() {
      return this.$route.params.serviceId
    },

    isLoading() {
      return this.$store.state.isLoading
    }
  },

  watch: {},

  created() {},

  methods: {}
}
</script>
<style lang="scss" scoped>
.w-180 {
  width: 180px;
}
</style>

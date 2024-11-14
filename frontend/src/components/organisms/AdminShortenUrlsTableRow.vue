<template>
  <tr
    @click="linkToDetail"
    class="u-clickable"
  >
    <td class="has-text-weight-semibold">
      <router-link :to="detailPageUrl">
        {{ padZero(shortenUrl.serviceSeqNumber) }}
      </router-link>
    </td>
    <td class="is-size-6">
      <div class="is-clipped max-w-800px">{{ shortenUrl.url }}</div>
    </td>
    <td class="is-size-7 has-text-success has-text-centered align-middle has-text-weight-semibold">
      <span
        v-if="shortenUrl.confirmStatus === 'confirmed'"
        class="has-text-success"
      >
        {{ $t('common.confirmed') }}
      </span>
      <span
        v-else
        class="has-text-danger"
      >
        {{ $t('common.unconfirmed') }}
      </span>
    </td>
    <!-- <td>
      <router-link
        v-if="hasEditorRole"
        :to="`/admin/shorten-urls/${serviceId}/${shortenUrl.urlId}/edit`"
        class="button is-small has-text-centered"
      >
        <span class="icon is-small">
          <i class="fas fa-pen"></i>
        </span>
      </router-link>

      <span v-else>-</span>
    </td> -->
    <td class="is-size-7 min-w-150px">
      <inline-time :datetime="shortenUrl.createdAt"></inline-time>
    </td>
  </tr>
</template>
<script>
import InlineTime from '@/components/atoms/InlineTime'
import { siteMixin } from '@/mixins/site'

export default {
  mixins: [siteMixin],

  components: {
    InlineTime
  },

  props: {
    shortenUrl: {
      type: Object,
      default: null
    }
  },

  computed: {
    serviceId() {
      return this.$route.params.serviceId
    },

    detailPageUrl() {
      return `/admin/shorten-urls/${this.serviceId}/${this.shortenUrl.urlId}`
    }
  },

  methods: {
    linkToDetail() {
      this.$router.push(this.detailPageUrl)
    }
  }
}
</script>

<style lang="scss">
.is-clipped {
  overflow: hidden !important;
  white-space: nowrap;
  text-overflow: ellipsis;
  width: 100%;
}
</style>

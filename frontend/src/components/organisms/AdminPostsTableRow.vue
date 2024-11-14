<template>
  <tr :class="rowBgColorClass">
    <td>
      <span
        v-if="publishStatus == 'unpublished'"
        class="tag is-danger mr-1"
        >{{ $t('common.unpublished') }}</span
      >
      <span
        v-else-if="publishStatus == 'reserved'"
        class="tag is-warning mr-1"
        >{{ $t('common.reserved') }}</span
      >
      <span
        v-else
        class="tag is-success mr-1"
        >{{ $t('common.published') }}</span
      >

      <span
        v-if="post.isHiddenInList"
        class="tag is-dark"
        >{{ $t('common.hidden') }}</span
      >
    </td>
    <td>
      <router-link :to="`/admin/posts/${serviceId}/${post.postId}`">{{ post.title }}</router-link>
    </td>
    <td
      class="is-size-7"
      v-text="getCategoryLabel(post.categorySlug)"
    ></td>
    <td>
      <router-link
        v-if="hasEditorRole"
        :to="`/admin/posts/${serviceId}/${post.postId}/edit`"
        class="button is-small"
      >
        <span class="icon is-small">
          <i class="fas fa-pen"></i>
        </span>
      </router-link>

      <span v-else>-</span>
    </td>
    <td class="is-size-7"><inline-time :datetime="post.publishAt"></inline-time></td>
    <td class="is-size-7"><inline-time :datetime="post.createdAt"></inline-time></td>
    <td class="is-size-7"><inline-time :datetime="post.updatedAt"></inline-time></td>
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
    post: {
      type: Object,
      default: null
    }
  },

  data() {
    return {}
  },

  computed: {
    publishStatus() {
      return this.getPostPublishStatus(this.post.statusPublishAt)
    },

    categoryLabel() {
      if ('category' in this.post === false) return '-'
      if (this.checkEmpty(this.post.category)) return '-'
      if (this.checkEmpty(this.post.category.label)) return '-'
      return this.post.category.label
    },

    rowBgColorClass() {
      switch (this.publishStatus) {
        case 'unpublished':
          return 'has-background-danger-light'
        case 'reserved':
          return 'has-background-warning-light'
      }
      if (this.post.isHiddenInList === true) return 'has-background-light'
      return ''
    }
  },

  watch: {},

  created() {},

  methods: {}
}
</script>

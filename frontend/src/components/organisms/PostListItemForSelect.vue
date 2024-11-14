<template>
  <div class="media">
    <span class="media-left">
      <button
        @click="selectPost(post)"
        :disabled="selectDisabled"
        class="button is-small"
      >
        <span class="icon is-small">
          <i class="fas fa-plus"></i>
        </span>
        <span>{{ $t('common.select') }}</span>
      </button>
    </span>
    <div class="media-content">
      <div>{{ post.title }}</div>
      <div class="is-size-7">
        <span>{{ $t('common.publishAt') }}</span>
        <span>{{ dateFormat(post.publishAt) }}</span>
      </div>
    </div>
  </div>
</template>
<script>
import utilDate from '@/util/date'

export default {
  props: {
    post: {
      type: Object,
      default: null
    },

    selectDisabled: {
      type: Boolean,
      default: false
    }
  },

  methods: {
    selectPost(post) {
      this.$emit('select', post)
    },

    dateFormat(date) {
      return utilDate.localeStrFromUtcDate(date)
    }
  }
}
</script>

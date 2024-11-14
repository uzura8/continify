<template>
  <div class="card">
    <div class="card-content">
      <div class="media">
        <div class="media-content">
          <h4 class="title is-4">
            <router-link :to="`/posts/${serviceId}/${post.slug}`">{{ post.title }}</router-link>
          </h4>
        </div>
      </div>

      <div class="content">
        <div v-text="post.bodyText"></div>
        <div class="mt-5">
          <time
            itemprop="datepublished"
            :datetime="dateFormat(post.publishAt)"
          >
            {{ dateFormat(post.publishAt) }}
          </time>
        </div>
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
    }
  },

  computed: {
    serviceId() {
      return this.post.serviceId
    }
  },

  methods: {
    dateFormat(date) {
      return utilDate.localeStrFromUtcDate(date)
    }
  }
}
</script>

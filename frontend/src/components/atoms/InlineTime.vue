<template>
<span>
  <time
    v-if="isEmptyDatetime === false"
    itemprop="time"
    :datetime="dateFormat(datetime, format)"
    :class="timeClass"
  >{{ dateFormat(datetime, format) }}</time>
  <span v-else>-</span>
</span>
</template>
<script>
import { siteMixin } from '@/mixins/site'

export default{
  mixins: [siteMixin],

  props: {
    datetime: {
      type: String,
      default: '',
    },

    format: {
      type: String,
      default: '',
    },

    timeClass: {
      type: String,
      default: '',
    },
  },

  computed: {
    isEmptyDatetime() {
      if (this.checkEmpty(this.datetime)) return true
      if (this.datetime === 'None') return true
      return false
    },
  },
}
</script>


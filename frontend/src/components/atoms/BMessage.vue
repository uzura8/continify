<template>
  <div
    class="notification"
    :class="type"
  >
    <slot />
  </div>
</template>
<script>
export default {
  props: {
    type: {
      type: String,
      default: ''
    }
  },

  data() {
    return {}
  },
  created() {}
}
</script>

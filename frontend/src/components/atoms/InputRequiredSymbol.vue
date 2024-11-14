<script>
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    isUsedInLabel: {
      type: Boolean,
      default: true
    }
  }
})
</script>

<template>
  <span
    class="has-text-danger"
    :class="{ 'ml-2': isUsedInLabel }"
  >
    *
  </span>
</template>

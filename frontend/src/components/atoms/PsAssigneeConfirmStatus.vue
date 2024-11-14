<template>
  <span>
    <span
      v-if="isConfirmed"
      class="has-text-success has-text-weight-semibold"
    >
      <span class="icon">
        <i class="fas fa-check-circle"></i>
      </span>
      {{ $t('shortenUrl.term.assigneeConfirmedYes') }}
    </span>
    <span
      v-else
      class="has-text-danger-dark has-text-weight-semibold"
    >
      <span class="icon">
        <i class="fas fa-exclamation-triangle"></i>
      </span>
      {{ $t('shortenUrl.term.assigneeConfirmedNo') }}
    </span>
  </span>
</template>
<script>
export default {
  components: {},

  props: {
    isConfirmed: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {}
  },

  computed: {},

  created() {},

  methods: {}
}
</script>

<template>
<div class="dropdown" :class="[{ 'is-active': isActive }, position]">
  <div class="dropdown-trigger">
    <button
      @click="isActive = !isActive"
      class="button"
      :class="btnClass"
      aria-haspopup="true"
      aria-controls="dropdown-menu"
    >
      <slot name="label"></slot>
      <span
        v-if="!hiddenCaret"
        class="icon is-small"
      >
        <i class="fas fa-angle-down" aria-hidden="true"></i>
      </span>
    </button>
  </div>
  <div class="dropdown-menu" id="dropdown-menu" role="menu">
    <slot></slot>
  </div>
</div>
</template>

<script>
import listener from '@/listener'

export default {
  props: {
    position: {
      type: String,
      default: '',
    },

    btnClass: {
      type: String,
      default: '',
    },

    btnClass: {
      type: String,
      default: '',
    },

    hiddenCaret: {
      type: Boolean,
      default: false,
    },
  },

  data(){
    return {
      isActive: false,
    }
  },

  computed: {
    parentBtnClass() {
      return {
        'is-active': this.isActive,
        active: true,
        'text-danger': false
      }
    },
  },

  created() {
    listener.listen(window, 'click', function(e){
      if (!this.$el.contains(e.target)) {
        this.isActive = false
      }
    }.bind(this));
  },

  methods: {
    destroyedComponent: listener.destroyed,
  },
}
</script>

<style lang="scss" scoped>
</style>

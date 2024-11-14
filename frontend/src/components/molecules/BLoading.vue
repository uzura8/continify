<template>
  <div
    v-if="active"
    class="loader-wrapper"
    :class="{ 'is-fullscreen': isFullPage }"
  >
    <div
      class="loader"
      :class="{ 'is-loading': active }"
    ></div>
  </div>
</template>
<script>
export default {
  props: {
    active: {
      type: Boolean,
      default: false
    },
    isFullPage: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {}
  }
}
</script>

<style lang="scss">
.loader-wrapper {
  width: 100%;
  height: 100%;
  z-index: 9999;
  background-color: rgba(255, 255, 255, 0.5); // Semi-transparent white
  position: absolute;
  top: 0;
  left: 0;

  &.is-fullscreen {
    position: fixed;
    width: 100vw; // Viewport width
    height: 100vh; // Viewport height
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }

  .loader {
    width: 50px;
    height: 50px;
    border: 6px solid #f3f3f3; // Light grey
    border-top: 6px solid #6aabd6; // Blue

    border-radius: 50%;
    position: absolute;
    top: calc(50% - 25px);
    left: calc(50% - 25px);
    transform: translate(-50%, -50%);
    animation: spin 0.75s linear infinite;
    opacity: 0;
    transition: opacity 0.3s ease;

    &.is-loading {
      opacity: 1;
    }
  }
}

@keyframes spin {
  0% {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  100% {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}
</style>

<template>
  <Dialog
    :visible="modelValue"
    modal
    :header="headerLabel"
    :style="{ width: '50vw' }"
    :closable="false"
    :dismissableMask="true"
  >
    <slot></slot>

    <template #footer>
      <button
        class="button"
        @click="$emit('close')"
      >
        {{ cancelButtonLabel }}
      </button>
      <button
        class="button"
        :class="executeButtonType"
        @click="$emit('execute')"
      >
        {{ executeButtonLabel }}
      </button>
    </template>
  </Dialog>
</template>
<script>
import 'primevue/resources/themes/lara-light-indigo/theme.css'
import 'primevue/resources/primevue.min.css'
import Dialog from 'primevue/dialog'

export default {
  components: {
    Dialog
  },

  props: {
    modelValue: {
      type: Boolean,
      required: true,
      default: false
    },
    executeButtonLabel: {
      type: String,
      required: false,
      default: 'OK'
    },
    executeButtonType: {
      type: String,
      required: false,
      default: 'is-info'
    },
    cancelButtonLabel: {
      type: String,
      required: false,
      default: 'Cancel'
    },
    headerLabel: {
      type: String,
      required: false,
      default: ''
    }
  }
}
</script>

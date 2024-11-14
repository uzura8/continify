<template>
  <Dialog
    :visible="modelValue"
    modal
    :header="headerLabel"
    :style="{ width: '50vw' }"
    @hide="console.log('hide')"
    @close="console.log('close')"
    :closable="true"
    :dismissableMask="true"
  >
    <slot></slot>

    <template #footer>
      <button
        class="button"
        @click="$emit('close')"
      >
        {{ $t('common.close') }}
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
    headerLabel: {
      type: String,
      required: false,
      default: ''
    }
  }
}
</script>

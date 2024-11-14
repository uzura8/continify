<script>
import { computed } from 'vue'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import utilDate from '@/util/date'

export default {
  components: {
    VueDatePicker
  },

  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },

  emits: ['update:modelValue'],

  setup(props, context) {
    const value = computed({
      get() {
        if (props.modelValue) {
          return new Date(props.modelValue)
        }
        return null
      },
      set(value) {
        let dateStr = ''
        if (value) {
          dateStr = utilDate.utcDateStrFromJsDate(value)
        }
        context.emit('update:modelValue', dateStr)
      }
    })

    const format = computed(() => {
      if (!value.value) {
        return ''
      }
      const year = value.value.getFullYear()
      const month = String(value.value.getMonth() + 1).padStart(2, '0')
      const day = String(value.value.getDate()).padStart(2, '0')
      const hours = String(value.value.getHours()).padStart(2, '0')
      const minutes = String(value.value.getMinutes()).padStart(2, '0')
      return `${year}/${month}/${day} ${hours}:${minutes}`
    })

    return {
      value,
      format
    }
  }
}
</script>

<template>
  <VueDatePicker
    v-model="value"
    locale="jp"
    :format="format"
    show-now-button
    placeholder="Select Date"
  />
</template>

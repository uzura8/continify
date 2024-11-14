<script>
import { ref, computed, watch, nextTick } from 'vue'

export default {
  props: {
    modelValue: {
      type: [Number, String],
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    },
    lazy: {
      type: Boolean,
      default: false
    },
    passwordReveal: Boolean,
    iconClickable: Boolean,
    customClass: {
      type: String,
      default: ''
    }
  },

  setup(props, { emit }) {
    const newValue = ref(props.modelValue)
    const isPasswordVisible = ref(false)
    const newType = ref(props.type)

    const computedValue = computed({
      get: () => newValue.value,
      set: (value) => {
        newValue.value = value
        emit('input', value)
      }
    })

    const inputClasses = computed(() => [])

    watch(
      () => props.modelValue,
      (value) => {
        newValue.value = value
      }
    )

    watch(
      () => props.type,
      (type) => {
        newType.value = type
      }
    )

    const onInput = (event) => {
      if (!props.lazy) {
        const value = event.target.value
        updateValue(value)
      }
    }

    const onChange = (event) => {
      if (props.lazy) {
        const value = event.target.value
        updateValue(value)
      }
    }

    const updateValue = (value) => {
      computedValue.value = value
    }

    const togglePasswordVisibility = () => {
      isPasswordVisible.value = !isPasswordVisible.value
      newType.value = isPasswordVisible.value ? 'text' : 'password'
      nextTick(() => {
        focus()
      })
    }

    const focus = () => {
      //focus handling
    }

    const iconClick = (emitName, event) => {
      emit(emitName, event)
      nextTick(() => {
        focus()
      })
    }

    const rightIconClick = (event) => {
      if (props.passwordReveal) {
        togglePasswordVisibility()
      } else if (props.iconRightClickable) {
        iconClick('icon-right-click', event)
      }
    }

    return {
      newValue,
      isPasswordVisible,
      newType,
      computedValue,
      inputClasses,
      onInput,
      onChange,
      updateValue,
      togglePasswordVisibility,
      focus,
      iconClick,
      rightIconClick
    }
  }
}
</script>

<template>
  <div class="control">
    <input
      v-if="type !== 'textarea'"
      type="text"
      class="input"
      :class="[inputClasses, customClass]"
      v-model="newValue"
      v-bind="$attrs"
      @change="onChange"
      @blur="onBlur"
      @focus="onFocus"
    />
    <textarea
      v-else
      ref="textarea"
      class="textarea"
      :class="[inputClasses, customClass]"
      v-model="newValue"
      v-bind="$attrs"
      @change="onChange"
      @blur="onBlur"
      @focus="onFocus"
    />
  </div>
</template>

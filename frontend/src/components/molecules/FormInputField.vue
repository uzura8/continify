<script>
import { defineComponent, ref, watch, computed } from 'vue'
import InputRequiredSymbol from '@/components/atoms/InputRequiredSymbol.vue'

export default defineComponent({
  components: {
    InputRequiredSymbol
  },

  props: {
    inputType: {
      type: String,
      default: 'text'
    },
    inputClass: {
      type: String,
      default: ''
    },
    isWidthFull: {
      type: Boolean,
      default: false
    },
    labelText: {
      type: String,
      required: false,
      default: ''
    },
    errorText: {
      type: String,
      default: ''
    },
    helperText: {
      type: String,
      default: ''
    },
    helperTexts: {
      type: Array,
      default: () => []
    },
    isRequired: {
      type: Boolean,
      default: false
    },
    textAreaRows: {
      type: Number,
      default: 3
    },
    isDisplayTextCounter: {
      type: Boolean,
      default: false
    },
    maxTextCount: {
      type: Number,
      default: 0
    },
    modelValue: {
      type: String,
      required: false,
      default: ''
    }
  },

  emits: ['update:modelValue', 'blur'],

  setup(props, context) {
    const inputValue = ref(props.modelValue)

    const inputClassStr = computed(() => {
      let classes = props.inputClass ? props.inputClass.split(' ') : []
      if (props.isWidthFull) {
        classes.push('w-full')
      }
      if (props.errorText) {
        classes = classes.concat(['is-danger'])
      } else {
        classes = classes.concat(['border-gray-300'])
      }
      return classes.join(' ')
    })

    const textCount = computed(() => {
      if (inputValue.value == null) {
        return 0
      }
      return inputValue.value.length
    })

    watch(
      () => props.modelValue,
      (value) => {
        inputValue.value = value
      }
    )

    watch(inputValue, (value) => {
      context.emit('update:modelValue', value)
    })

    return {
      inputValue,
      inputClassStr,
      textCount
    }
  }
})
</script>

<template>
  <div class="field">
    <label
      v-if="labelText"
      class="label"
    >
      <span>{{ labelText }}</span>
      <InputRequiredSymbol v-if="isRequired" />
    </label>
    <textarea
      v-if="inputType === 'textarea'"
      v-model="inputValue"
      :type="inputType"
      :rows="textAreaRows"
      class="w-full textarea"
      :class="{
        'is-danger': errorText || (isDisplayTextCounter && maxTextCount && textCount > maxTextCount)
      }"
      @blur="$emit('blur', inputValue)"
    ></textarea>

    <input
      v-else
      v-model="inputValue"
      type="text"
      class="input"
      :class="inputClassStr"
      @blur="$emit('blur', inputValue)"
    />
    <div
      v-if="isDisplayTextCounter"
      class="pt-1"
    >
      <span
        v-if="maxTextCount"
        class="flex justify-end gap-x-1"
      >
        <span>{{ textCount }}</span>
        <span>/</span>
        <span>{{ maxTextCount }}</span>
      </span>
      <span v-else>
        <span>{{ textCount }}</span>
      </span>
    </div>
    <p
      v-if="errorText"
      class="help is-danger"
      :class="{ 'mt-2': !isDisplayTextCounter }"
    >
      {{ errorText }}
    </p>
    <p
      v-if="helperText"
      class="help"
    >
      {{ helperText }}
    </p>
    <div
      v-if="helperTexts"
      class="mt-2 help"
    >
      <div
        v-for="(item, index) in helperTexts"
        :key="index"
        :class="{ 'mt-2': index > 0 }"
      >
        {{ item }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.input {
  width: auto;
}
.w-full {
  width: 100%;
}
.block {
  display: block !important;
}
</style>

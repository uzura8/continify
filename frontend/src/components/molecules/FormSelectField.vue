<script>
import { computed, defineComponent, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import InputRequiredSymbol from '@/components/atoms/InputRequiredSymbol.vue'

export default defineComponent({
  components: {
    InputRequiredSymbol
  },

  props: {
    labelText: {
      type: String,
      required: false,
      default: ''
    },
    options: {
      type: Array,
      required: false,
      default: () => []
    },
    optionObjs: {
      type: Array,
      required: false,
      default: () => []
    },
    defaultOptionText: {
      type: String,
      required: false,
      default: ''
    },
    errorText: {
      type: String,
      required: false,
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
    optionsLabelTransKey: {
      type: String,
      required: false,
      default: ''
    },
    isWidthFull: {
      type: Boolean,
      required: false,
      default: false
    },
    isRequired: {
      type: Boolean,
      required: false,
      default: false
    },
    hasError: {
      type: Boolean,
      required: false,
      default: false
    },
    modelValue: {
      type: String,
      required: false,
      default: ''
    }
  },

  emits: ['update:modelValue', 'change'],

  setup(props, context) {
    console.log('props', props.options)
    const { t } = useI18n()

    const selectedValue = ref(props.modelValue)

    watch(
      () => props.modelValue,
      (value) => {
        selectedValue.value = value
      }
    )

    watch(selectedValue, (value, oldValue) => {
      context.emit('update:modelValue', value)
      context.emit('change', value, oldValue)
    })

    const optionText = (key) => {
      if (!props.optionsLabelTransKey) return key
      return t(`${props.optionsLabelTransKey}.${key}`)
    }

    const isApplyErrorStyle = computed(() => {
      return props.errorText.length > 0 || props.hasError
    })

    return {
      selectedValue,
      optionText,
      isApplyErrorStyle
    }
  }
})
</script>

<template>
  <div class="field">
    <label
      v-if="labelText"
      class="label"
      :class="{ 'text-danger-700 dark:text-danger-500': isApplyErrorStyle }"
    >
      <span>{{ labelText }}</span>
      <InputRequiredSymbol v-if="isRequired" />
    </label>

    <div class="control">
      <div
        class="select"
        :class="{ 'is-danger': isApplyErrorStyle, 'w-full': isWidthFull }"
      >
        <select
          v-model="selectedValue"
          :class="{ 'w-full': isWidthFull }"
        >
          <option
            v-if="defaultOptionText"
            value=""
          >
            {{ defaultOptionText }}
          </option>

          <template v-if="optionObjs && optionObjs.length > 0">
            <option
              v-for="optionObj in optionObjs"
              :key="optionObj.value"
              :value="optionObj.value"
              v-text="optionObj.label"
            ></option>
          </template>

          <template v-else-if="options && options.length > 0">
            <option
              v-for="optionValue in options"
              :key="optionValue"
              :value="optionValue"
              v-text="optionText(optionValue)"
            ></option>
          </template>
        </select>
      </div>
    </div>
    <p
      v-if="errorText"
      class="help is-danger"
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
      class="mt-2"
    >
      <div
        v-for="(item, index) in helperTexts"
        :key="index"
        class="help"
        :class="{ 'mt-2': index > 0 }"
      >
        {{ item }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.block {
  display: block !important;
}
</style>

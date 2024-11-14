<template>
  <div
    class="control"
    :class="{ 'is-expanded': expanded, 'has-icons-left': icon }"
  >
    <span
      class="select"
      :class="spanClasses"
    >
      <select
        :modelValue="selected"
        ref="select"
        :multiple="multiple"
        :size="nativeSize"
        v-bind="$attrs"
        @blur="emitBlurAndCheckValidity($event)"
        @focus="$emit('focus', $event)"
        @change="onChange"
      >
        <template v-if="placeholder">
          <option
            v-if="selected == null"
            :value="null"
            disabled
            hidden
          >
            {{ placeholder }}
          </option>
        </template>

        <slot />
      </select>
    </span>
  </div>
</template>

<script>
import FormElementMixin from '@/util/buefy/mixins/FormElementMixin'

export default {
  mixins: [FormElementMixin],
  inheritAttrs: false,
  props: {
    modelValue: {
      type: [String, Number, Boolean, Object, Array, Function, Date],
      default: null
    },
    placeholder: String,
    multiple: Boolean,
    nativeSize: [String, Number]
  },
  data() {
    return {
      selected: this.modelValue,
      _elementRef: 'select'
    }
  },
  computed: {
    spanClasses() {
      return [
        this.size,
        this.statusType,
        {
          'is-fullwidth': this.expanded,
          'is-loading': this.loading,
          'is-multiple': this.multiple,
          'is-rounded': this.rounded,
          'is-empty': this.selected === null
        }
      ]
    }
  },
  methods: {
    emitBlurAndCheckValidity(event) {
      this.$emit('blur', event)
      this.checkHtml5Validity()
    },
    onChange(event) {
      this.selected = event.target.value
      this.$emit('update:modelValue', this.selected)
      !this.isValid && this.checkHtml5Validity()
    }
  },
  watch: {
    modelValue(value) {
      this.selected = value
      !this.isValid && this.checkHtml5Validity()
    }
  }
}
</script>

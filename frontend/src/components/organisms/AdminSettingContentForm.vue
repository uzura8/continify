<script>
import { ref, onBeforeMount, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import utilStr from '@/util/str'
import FormInputField from '@/components/molecules/FormInputField.vue'
import FormSelectField from '@/components/molecules/FormSelectField.vue'

export default {
  components: {
    FormInputField,
    FormSelectField
  },

  props: {
    defaultPublishStatus: {
      type: String,
      required: false,
      default: ''
    },
    content: {
      type: Object,
      required: false,
      default: () => {}
    }
  },

  emits: ['update', 'cancel'],

  setup(props, context) {
    const { t } = useI18n()

    const isEdit = computed(() => {
      if (!props.content) return false
      return !!props.content.contentId
    })

    const errors = ref({
      commentDefaultPublishStatus: ''
    })
    if (!isEdit.value) {
      errors.value.contentId = ''
    }

    const contentId = ref('')
    const validateContentId = () => {
      errors.value.contentId = ''
      contentId.value = contentId.value.trim()
      if (contentId.value === '') {
        errors.value.contentId = t('msg.inputRequired')
      } else if (!utilStr.checkKeyString(contentId.value)) {
        errors.value.contentId = t('msg.InvalidInput')
      } else if (contentId.value.length < 4) {
        errors.value.contentId = t('msg.inputAtLeastTargetCharacters', { num: 4 })
      } else if (contentId.value.length > 32) {
        errors.value.contentId = t('msg.inputNoMoreThanTargetCharacters', { num: 32 })
      }
    }

    const commentDefaultPublishStatus = ref(props.defaultPublishStatus)
    const commentDefaultPublishStatusList = ['unpublish', 'publish']
    const validateDefaultPublishStatus = () => {
      errors.value.commentDefaultPublishStatus = ''
      if (!commentDefaultPublishStatus.value) {
        errors.value.commentDefaultPublishStatus = t('msg.inputRequired')
      } else if (!commentDefaultPublishStatusList.includes(commentDefaultPublishStatus.value)) {
        errors.value.commentDefaultPublishStatus = t('msg.InvalidInput')
      }
    }

    const validateAll = () => {
      validateContentId()
      validateDefaultPublishStatus()
    }

    const resetAll = () => {
      contentId.value = ''
      commentDefaultPublishStatus.value = ''
      errors.value.contentId = ''
      errors.value.commentDefaultPublishStatus = ''
    }

    const hasErrors = computed(() => {
      return Object.values(errors.value).some((error) => error !== '')
    })

    const updatedVals = computed(() => {
      return {
        contentId: contentId.value,
        commentDefaultPublishStatus: commentDefaultPublishStatus.value
      }
    })

    const update = () => {
      validateAll()
      if (hasErrors.value) return
      context.emit('update', updatedVals.value)
      resetAll()
    }

    const cancel = () => {
      context.emit('cancel')
      resetAll()
    }

    onBeforeMount(async () => {})

    return {
      isEdit,
      errors,
      contentId,
      commentDefaultPublishStatus,
      commentDefaultPublishStatusList,
      validateContentId,
      validateDefaultPublishStatus,
      validateAll,
      hasErrors,
      update,
      cancel
    }
  }
}
</script>

<template>
  <div>
    <h3 class="title is-4">
      {{ isEdit ? $t('common.edit') : $t('common.create') }}
    </h3>
    <FormInputField
      v-if="!isEdit"
      v-model="contentId"
      :label-text="$t('term.contentId')"
      :is-required="true"
      :error-text="errors.contentId"
      @blur="validateContentId"
    />

    <FormSelectField
      v-model="commentDefaultPublishStatus"
      :label-text="$t('form.commentDefaultPublishStatus.label')"
      :options="commentDefaultPublishStatusList"
      :options-label-trans-key="'form.commentDefaultPublishStatus'"
      :default-option-text="$t('msg.pleaseSelect')"
      :is-required="true"
      :error-text="errors.commentDefaultPublishStatus"
      class="mt-5 mb-6"
      @change="validateDefaultPublishStatus"
    />

    <div
      v-if="hasErrors"
      class="block has-text-danger mb-3"
    >
      {{ $t('msg.ErrorsExist') }}
    </div>

    <div class="field">
      <div class="control">
        <button
          class="button is-info"
          @click="update"
          v-text="isEdit ? $t('common.create') : $t('common.create')"
        ></button>
      </div>
    </div>

    <div class="field">
      <div class="control">
        <button
          class="button is-light"
          @click="cancel"
          v-text="$t('common.cancel')"
        ></button>
      </div>
    </div>
  </div>
</template>

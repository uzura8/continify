<script>
import { ref } from 'vue'
// import { useStore } from 'vuex'
// import { useI18n } from 'vue-i18n'
// import { useAdminAuth } from '@/composables/useAdminAuth'
// import { useApiError } from '@/composables/useApiError'
// import { Admin } from '@/api'
// import AdminSettingContentForm from '@/components/organisms/AdminSettingContentForm'
import EbDialog from '@/components/molecules/EbDialog'

export default {
  components: {
    EbDialog
  },

  props: {
    content: {
      type: Object,
      required: true
    }
  },

  emits: ['delete', 'update-publish-status'],

  setup(props, context) {
    // const store = useStore()
    // const { t } = useI18n()
    // const { handleApiError } = useApiError()
    // const { checkAndRefreshTokens } = useAdminAuth()

    const isConfirmDeleteDialogActive = ref(false)
    const deleteContent = () => {
      isConfirmDeleteDialogActive.value = false
      context.emit('delete', props.content.contentId)
    }

    const isConfirmUpdatePublishStatusDialogActive = ref(false)
    const updatePublishStatus = () => {
      const status =
        props.content.commentDefaultPublishStatus === 'publish' ? 'unpublish' : 'publish'
      const payload = {
        contentId: props.content.contentId,
        publishStatus: status
      }
      isConfirmUpdatePublishStatusDialogActive.value = false
      context.emit('update-publish-status', payload)
    }

    return {
      isConfirmUpdatePublishStatusDialogActive,
      updatePublishStatus,
      isConfirmDeleteDialogActive,
      deleteContent
    }
  }
}
</script>

<template>
  <div class="box">
    <h3 class="is-flex is-justify-content-space-between">
      <div>
        <span class="mr-2 has-text-weight-normal is-size-7">contentId</span>
        <span class="is-size-4 has-text-weight-semibold">{{ content.contentId }}</span>
      </div>
      <div>
        <button
          class="button is-ghost"
          @click="isConfirmDeleteDialogActive = true"
        >
          {{ $t('common.delete') }}
        </button>
        <EbDialog
          v-model="isConfirmDeleteDialogActive"
          :header-label="$t('common.confirmTo', { action: $t('common.delete') })"
          :execute-button-label="$t('common.delete')"
          execute-button-type="is-danger"
          @execute="deleteContent()"
          @close="isConfirmDeleteDialogActive = false"
        >
          <p>{{ $t('msg.cofirmToDelete') }}</p>
        </EbDialog>
      </div>
    </h3>
    <div>
      <div class="is-flex is-align-items-center">
        <label class="is-size-7 has-text-weight-semibold has-text-grey mr-2">
          {{ $t('form.commentDefaultPublishStatus.label') }}
        </label>
        <div
          :class="{
            'has-text-success': content.commentDefaultPublishStatus === 'publish',
            'has-text-danger': content.commentDefaultPublishStatus === 'unpublish'
          }"
        >
          {{ $t(`form.commentDefaultPublishStatus.${content.commentDefaultPublishStatus}`) }}
        </div>
        <button
          class="button is-ghost ml-1"
          @click="isConfirmUpdatePublishStatusDialogActive = true"
        >
          {{ $t('common.change') }}
        </button>
        <EbDialog
          v-model="isConfirmUpdatePublishStatusDialogActive"
          :header-label="$t('common.confirmTo', { action: $t('common.change') })"
          :execute-button-label="$t('common.doChange')"
          execute-button-type="is-warning"
          @execute="updatePublishStatus"
          @close="isConfirmUpdatePublishStatusDialogActive = false"
        >
          <div>
            <p class="py-1">
              {{ $t('msg.changeFor', { target: $t('form.commentDefaultPublishStatus.label') }) }}
            </p>
            <p class="py-1">{{ $t('comment.msg.cautionBeforeUpdateDefaultPublishStatus') }}</p>
            <p class="py-1">{{ $t('msg.ConfirmBeforeExec') }}</p>
          </div>
        </EbDialog>
      </div>
    </div>
    <div class="is-flex mt-3">
      <RouterLink
        :to="`/admin/comments/${content.serviceId}/content/${content.contentId}`"
        class=""
      >
        {{ $t('comment.page.commentList') }}
      </RouterLink>
    </div>
  </div>
</template>

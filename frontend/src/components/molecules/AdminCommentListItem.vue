<script>
import { ref, computed } from 'vue'
import utilStr from '@/util/str'
import InlineTime from '@/components/atoms/InlineTime'
import EbDialog from '@/components/molecules/EbDialog'
import EbDropdown from '@/components/molecules/EbDropdown'

export default {
  components: {
    InlineTime,
    EbDialog,
    EbDropdown
  },

  props: {
    comment: {
      type: Object,
      required: true
    }
  },

  emits: ['updatePublishStatus', 'deleteComment'],

  setup(props, context) {
    const bodyHtml = computed(() => {
      if (!props.comment) return ''
      return convertToHTML(props.comment.body)
    })

    const convertToHTML = (text) => {
      return utilStr.url2link(utilStr.nl2br(text))
    }

    const updatePublishStatus = (status) => {
      const payload = {
        commentId: props.comment.commentId,
        publishStatus: status
      }
      context.emit('updatePublishStatus', payload)
    }

    const hasProfiles = computed(() => {
      return (
        props.comment.profiles && Object.values(props.comment.profiles).some((value) => !!value)
      )
    })

    const isConfirmDeleteDialogActive = ref(false)
    const deleteComment = () => {
      context.emit('deleteComment', props.comment.commentId)
    }

    return {
      bodyHtml,
      hasProfiles,
      updatePublishStatus,
      isConfirmDeleteDialogActive,
      deleteComment
    }
  }
}
</script>

<template>
  <div class="card">
    <header class="card-header">
      <div class="card-header-title is-flex is-justify-content-space-between is-align-items-center">
        <div class="is-flex">
          <div>
            <label class="is-size-7 has-text-grey-light mr-1">ContentID:</label>
            <span class="has-text-weight-medium">{{ comment.contentId }}</span>
          </div>
        </div>
        <div>
          <eb-dropdown
            position="is-right"
            btn-class="is-white"
          >
            <template #label>
              <span class="icon">
                <i class="fas fa-ellipsis-h"></i>
              </span>
            </template>
            <div class="dropdown-content">
              <button
                class="button is-ghost"
                @click="isConfirmDeleteDialogActive = true"
              >
                {{ $t('common.delete') }}
              </button>
            </div>
          </eb-dropdown>
          <EbDialog
            v-model="isConfirmDeleteDialogActive"
            :header-label="$t('common.confirmTo', { action: $t('common.delete') })"
            :execute-button-label="$t('common.delete')"
            execute-button-type="is-danger"
            @execute="deleteComment()"
            @close="isConfirmDeleteDialogActive = false"
          >
            <p>{{ $t('msg.cofirmToDelete') }}</p>
          </EbDialog>
        </div>
      </div>
    </header>

    <div class="card-content">
      <div class="content">
        <dl
          v-if="comment.createdAt || hasProfiles"
          class="def-list"
        >
          <div class="is-flex is-align-items-center mb-1">
            <dt class="has-text-weight-semibold is-size-7">
              {{ $t('comment.term.createdAt') }}
            </dt>
            <dd>
              <InlineTime :datetime="comment.createdAt" />
            </dd>
          </div>
          <div
            v-for="(value, key, index) in comment.profiles"
            :key="key"
            class="is-flex is-align-items-center"
            :class="{ 'mb-1': index !== Object.keys(comment.profiles).length - 1 }"
          >
            <dt class="has-text-weight-semibold is-size-7">
              {{ $t(`comment.profiles.${key}`) }}
            </dt>
            <dd>{{ value }}</dd>
          </div>
        </dl>
        <p class="user-comment-body">{{ comment.body }}</p>
      </div>
    </div>

    <footer class="card-footer">
      <span class="card-footer-item">
        <span
          v-if="comment.publishStatus === 'publish'"
          class="has-text-success has-text-weight-semibold"
        >
          {{ $t('common.published') }}
        </span>
        <span
          v-else-if="comment.publishStatus === 'unpublish'"
          class="has-text-danger has-text-weight-semibold"
        >
          {{ $t('common.unpublished') }}
        </span>
      </span>
      <a
        class="card-footer-item u-clickable"
        :class="{ 'cursor-not-allowed has-text-grey-light': comment.publishStatus === 'publish' }"
        @click="updatePublishStatus('publish')"
      >
        {{ $t('common.publish') }}
      </a>
      <a
        class="card-footer-item u-clickable"
        :class="{ 'cursor-not-allowed has-text-grey-light': comment.publishStatus === 'unpublish' }"
        @click="updatePublishStatus('unpublish')"
      >
        {{ $t('common.unpublish') }}
      </a>
    </footer>
  </div>
</template>

<style scoped lang="scss">
.user-comment-body {
  white-space: pre-wrap;
  background-color: #f9fafb;
  word-wrap: normal;
  overflow-x: auto;
  padding: 1em 1em;
}
.cursor-not-allowed {
  cursor: not-allowed;
}

.def-list {
  dt {
    min-width: 80px;
    flex-shrink: 0;
  }
  dd {
    flex-grow: 1;
  }
}
</style>

<script>
import { ref, onBeforeMount } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { useAdminAuth } from '@/composables/useAdminAuth'
import { useApiError } from '@/composables/useApiError'
import { Admin } from '@/api'
import AdminSettingContentForm from '@/components/organisms/AdminSettingContentForm'
import AdminSettingContentItem from '@/components/organisms/AdminSettingContentItem'

export default {
  components: {
    AdminSettingContentForm,
    AdminSettingContentItem
  },

  props: {
    serviceId: {
      type: String,
      required: true
    }
  },

  setup(props) {
    const store = useStore()
    const { t } = useI18n()
    const { handleApiError } = useApiError()
    const { checkAndRefreshTokens } = useAdminAuth()

    const contentList = ref([])

    const isFormActive = ref(false)

    const setContentList = async () => {
      await checkAndRefreshTokens()
      try {
        store.dispatch('setLoading', true)
        const res = await Admin.getServiceContentList(
          props.serviceId,
          null,
          store.state.adminUser.token
        )
        contentList.value = res.items || []
      } catch (err) {
        console.log(err)
        handleApiError(err, 'Failed to get data from server')
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    const updatePublishStatus = async (payload) => {
      const vals = { commentDefaultPublishStatus: payload.publishStatus }
      try {
        store.dispatch('setLoading', true)
        const item = await Admin.saveServiceContent(
          props.serviceId,
          payload.contentId,
          vals,
          store.state.adminUser.token
        )
        const index = contentList.value.findIndex((content) => content.contentId === item.contentId)
        if (index === -1) {
          contentList.value.push(item)
          throw new Error('Failed to update data')
        }
        contentList.value.splice(index, 1, item)
      } catch (err) {
        console.log(err)
        handleApiError(err, t('msg["Update failed"]'))
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    const save = async (vals) => {
      try {
        store.dispatch('setLoading', true)
        const item = await Admin.saveServiceContent(
          props.serviceId,
          vals.contentId,
          vals,
          store.state.adminUser.token
        )
        const index = contentList.value.findIndex((content) => content.contentId === item.contentId)
        if (index === -1) {
          contentList.value.push(item)
        } else {
          contentList.value.splice(index, 1, item)
        }
        isFormActive.value = false
      } catch (err) {
        console.log(err)
        handleApiError(err, t('msg["Create failed"]'))
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    const defaultPublishStatus = ref('')
    const setDefaultPublishStatus = async () => {
      try {
        const res = await Admin.getServiceConfig(
          props.serviceId,
          'commentDefaultPublishStatus',
          store.state.adminUser.token
        )
        if (res) {
          defaultPublishStatus.value = res.configVal
        }
      } catch (err) {
        console.log(err)
        handleApiError(err)
      }
    }

    const deleteContent = async (contentId) => {
      try {
        store.dispatch('setLoading', true)
        await Admin.deleteServiceContent(props.serviceId, contentId, store.state.adminUser.token)
        const idx = contentList.value.findIndex((content) => content.contentId === contentId)
        contentList.value.splice(idx, 1)
      } catch (err) {
        console.log(err)
        handleApiError(err, 'Failed to delete data')
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    onBeforeMount(async () => {
      setContentList()
      setDefaultPublishStatus()
    })

    return {
      contentList,
      deleteContent,
      isFormActive,
      defaultPublishStatus,
      updatePublishStatus,
      save
    }
  }
}
</script>

<template>
  <div>
    <div>
      <ul v-if="contentList.length">
        <li
          v-for="content in contentList"
          :key="content.contentId"
          class="mt-4"
        >
          <AdminSettingContentItem
            :content="content"
            @delete="deleteContent"
            @update-publish-status="updatePublishStatus"
          />
        </li>
      </ul>
      <div
        v-else
        class="py-4"
      >
        {{ $t('msg.noData') }}
      </div>
    </div>

    <div class="mt-6">
      <div v-if="isFormActive">
        <AdminSettingContentForm
          :default-publish-status="defaultPublishStatus"
          @update="save"
          @cancel="isFormActive = false"
        />
      </div>
      <div
        v-else
        class="mt-3"
      >
        <button
          class="button"
          @click="isFormActive = true"
        >
          {{ $t('common.createNew') }}
        </button>
      </div>
    </div>
  </div>
</template>

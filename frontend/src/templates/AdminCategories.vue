<template>
  <div>
    <h1 class="title">{{ $t('page.AdminPostCategoryManagement') }}</h1>

    <div
      v-if="hasEditorRole"
      class="block"
    >
      <a
        v-if="isUseModalForCreate"
        class="button"
        @click="isModalActive = true"
        >{{ $t('common.createNew') }}</a
      >
      <router-link
        v-else
        :to="{ path: `/admin/categories/${serviceId}/create`, query: { parent: 'root' } }"
        class="button"
        >{{ $t('common.createNew') }}</router-link
      >
    </div>

    <div>
      <CategoryListRecursive parent-category-slug="root" />
    </div>
  </div>
</template>
<script>
import CategoryListRecursive from '@/components/molecules/CategoryListRecursive'
import { siteMixin } from '@/mixins/site'

export default {
  mixins: [siteMixin],

  components: {
    CategoryListRecursive
  },

  data() {
    return {
      isUseModalForCreate: false,
      isModalActive: false
    }
  },

  created() {}
}
</script>

<template>
  <div class="">
    <draggable
      :group="`categoryGroup-${parentCategorySlug}`"
      :options="{ handle: '.handle' }"
      :list="categories"
      item-key="slug"
      @start="drag = true"
      @end="drag = false"
      @update="updateCategoriesOrder"
    >
      <template #item="{ element }">
        <div
          v-if="deletedCateSlugs.includes(element.slug) === false"
          class="list-box"
        >
          <button
            v-if="hasEditorRole"
            class="button is-small handle"
          >
            <span class="icon is-small">
              <i class="fas fa-sort"></i>
            </span>
          </button>
          <a
            @click="toggleBlock(element.slug)"
            class="u-clickable list-label has-text-black"
          >
            <span>{{ element.label }}</span>
            <span class="icon is-pulled-right">
              <i
                v-if="activeCateSlugs.includes(element.slug)"
                class="fas fa-angle-up"
              ></i>
              <i
                v-else
                class="fas fa-angle-down"
              ></i>
            </span>
          </a>
          <ul
            v-if="activeCateSlugs.includes(element.slug)"
            class="is-flex mb-3"
          >
            <li
              v-if="hasEditorRole"
              class="mr-5"
            >
              <router-link
                :to="{
                  path: `/admin/categories/${serviceId}/create`,
                  query: { parent: element.slug }
                }"
                class="icon-text is-size-6i has-text-grey"
              >
                <span class="icon">
                  <i class="fas fa-plus"></i>
                </span>
                <span>{{ $t('common.add') }}</span>
              </router-link>
            </li>
            <li
              v-if="hasEditorRole"
              class="mr-5"
            >
              <router-link
                :to="`/admin/categories/${serviceId}/${element.slug}/edit`"
                class="icon-text is-size-6 has-text-grey"
              >
                <span class="icon">
                  <i class="fas fa-edit"></i>
                </span>
                <span>{{ $t('common.edit') }}</span>
              </router-link>
            </li>
            <li
              v-if="hasEditorRole"
              class="mr-5"
            >
              <a
                @click="isConfirmDeleteDialogActive = true"
                class="u-clickable icon-text is-size-6 has-text-grey"
              >
                <span class="icon">
                  <i class="fas fa-trash"></i>
                </span>
                <span>{{ $t('common.delete') }}</span>
              </a>
            </li>
            <li class="mr-5">
              <router-link
                :to="{ path: `/admin/posts/${serviceId}`, query: { category: element.slug } }"
                class="u-clickable icon-text is-size-6 has-text-grey"
                >{{ $t('common.posts') }}</router-link
              >
            </li>
          </ul>

          <EbDialog
            v-model="isConfirmDeleteDialogActive"
            :header-label="$t('common.confirmTo', { action: $t('common.delete') })"
            :execute-button-label="$t('common.delete')"
            execute-button-type="is-danger"
            @execute="deleteCategory(element.slug)"
            @close="isConfirmDeleteDialogActive = false"
          >
            <p>{{ $t('msg.cofirmToDelete') }}</p>
          </EbDialog>

          <CategoryListRecursive
            v-if="activeCateSlugs.includes(element.slug)"
            :parent-category-slug="element.slug"
          />
        </div>
      </template>
    </draggable>
  </div>
</template>
<script>
import draggable from 'vuedraggable'
import EbDialog from '@/components/molecules/EbDialog'
import { Admin } from '@/api'
import CategoryListRecursive from '@/components/molecules/CategoryListRecursive'
import { siteMixin } from '@/mixins/site'

export default {
  name: 'CategoryListRecursive',

  mixins: [siteMixin],

  components: {
    draggable,
    EbDialog,
    CategoryListRecursive: () => import('@/components/molecules/CategoryListRecursive')
  },

  props: {
    parentCategorySlug: {
      type: String,
      required: true
    }
  },

  data() {
    return {
      drag: false,
      categories: [],
      activeCateSlugs: [],
      deletedCateSlugs: [],
      isConfirmDeleteDialogActive: false
    }
  },

  computed: {
    categoryIds() {
      if (this.checkEmpty(this.categories) === true) return []
      return this.categories.map((item) => item.id)
    }
  },

  watch: {},

  async created() {
    await this.setCategories(this.parentCategorySlug)
  },

  methods: {
    async setCategories(parentCateSlug) {
      this.$store.dispatch('setLoading', true)
      try {
        this.categories.splice(0, this.categories.length)
        const items = await Admin.getCategoryChildrenByParentSlug(
          this.serviceId,
          parentCateSlug,
          null,
          this.adminUserToken
        )
        items.map((item) => {
          this.categories.push(item)
        })
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async deleteCategory(cateSlug) {
      this.$store.dispatch('setLoading', true)
      try {
        await Admin.deleteCategory(this.serviceId, cateSlug, this.adminUserToken)
        this.deletedCateSlugs.push(cateSlug)
        this.isConfirmDeleteDialogActive = false
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Delete failed"]'))
      }
    },

    toggleBlock(cateSlug) {
      const index = this.activeCateSlugs.findIndex((item) => item === cateSlug)
      if (index === -1) {
        this.activeCateSlugs.push(cateSlug)
      } else {
        this.activeCateSlugs.splice(index, 1)
      }
    },

    async updateCategoriesOrder() {
      try {
        this.$store.dispatch('setLoading', true)
        const vals = { sortedIds: this.categoryIds }
        await Admin.updateCategoriesOrder(
          this.serviceId,
          this.parentCategorySlug,
          vals,
          this.adminUserToken
        )
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t(`msg["Delete failed"]`))
      }
    }
  }
}
</script>
<style>
.list-box {
  border-bottom: 1px solid #dbdbdb;
  position: relative;
  padding-left: 40px;

  &:last-child {
    border-bottom: none;
  }

  .list-label {
    display: block;
    padding: 15px 0;
    font-size: 1.25rem;
  }

  .handle {
    position: absolute;
    top: 15px;
    left: 0;
  }
}
</style>

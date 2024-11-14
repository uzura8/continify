<template>
<div>
  <h1 class="title">{{ $t('common.createNewOf', {label: $t('term.urlForQrCode')}) }}</h1>
  <AdminShortenUrlForm />
</div>
</template>
<script>
import AdminShortenUrlForm from '@/components/organisms/AdminShortenUrlForm'

export default{
  components: {
    AdminShortenUrlForm,
  },
}
</script>


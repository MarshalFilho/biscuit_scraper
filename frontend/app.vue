<template>
  <div>
    <NuxtPage />
    <ToastContainer />
    <ConfirmModal />
  </div>
</template>

<script setup>
import ToastContainer from '~/components/ToastContainer.vue'
import ConfirmModal from '~/components/ConfirmModal.vue'
</script>

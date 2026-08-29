<template>
  <div class="redirecting">
    <p>Redirecionando para o BiscuitInsights...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  router.replace('/')
})
</script>

<style scoped>
.redirecting {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-family: sans-serif;
  color: #64748b;
}
</style>

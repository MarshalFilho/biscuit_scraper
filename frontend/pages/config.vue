<template>
  <div class="container">
    <Navbar :projectName="nomeProjeto" @auth-change="user => authUser = user" />

    <div class="config-page-header">
      <h2>⚙️ Central de Configurações & Automação</h2>
      <p class="subtitle">Gerencie regras de raspagem, palavras negativas, categorias e disparo do robô em nuvem.</p>
    </div>

    <div class="admin-panels">
      <ScraperConfig :user="authUser" @update-blacklist="onUpdateBlacklist" @update-project-name="name => nomeProjeto = name" />
      <CategoryManager :user="authUser" @update-categories="onUpdateCategories" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Navbar from '~/components/Navbar.vue'
import ScraperConfig from '~/components/ScraperConfig.vue'
import CategoryManager from '~/components/CategoryManager.vue'

const authUser = ref(null)
const nomeProjeto = ref('Scraper Pro')

function onUpdateBlacklist(list) {
  // Configs atualizadas
}

function onUpdateCategories(rules) {
  // Regras atualizadas
}
</script>

<style scoped>
.config-page-header {
  margin-bottom: 2rem;
}
.config-page-header h2 {
  font-size: 1.8rem;
  color: #0f172a;
  margin-bottom: 0.3rem;
}
.subtitle {
  color: #64748b;
  font-size: 1rem;
}
.admin-panels {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>

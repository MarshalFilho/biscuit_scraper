<template>
  <div class="container">
    <Navbar :projectName="nomeProjeto" @auth-change="user => authUser = user" />

    <div class="config-page-header">
      <h2>⚙️ Central de Configurações & Automação com IA</h2>
      <p class="subtitle">Gerencie regras de raspagem, palavras negativas, categorias, assistente de linguagem natural e disparo do robô na nuvem.</p>
    </div>

    <!-- Assistente de Filtros por IA (Fase 4) -->
    <AiFilterAssistant @apply-filters="handleApplyAiFilters" />

    <div class="admin-panels">
      <ScraperConfig ref="scraperConfigRef" :user="authUser" @update-blacklist="onUpdateBlacklist" @update-project-name="name => nomeProjeto = name" />
      <CategoryManager :user="authUser" @update-categories="onUpdateCategories" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Navbar from '~/components/Navbar.vue'
import ScraperConfig from '~/components/ScraperConfig.vue'
import CategoryManager from '~/components/CategoryManager.vue'
import AiFilterAssistant from '~/components/AiFilterAssistant.vue'

const authUser = ref(null)
const nomeProjeto = ref('Scraper Pro')
const scraperConfigRef = ref(null)

function handleApplyAiFilters(aiData) {
  if (scraperConfigRef.value && scraperConfigRef.value.applyAiGeneratedFilters) {
    scraperConfigRef.value.applyAiGeneratedFilters(aiData)
  }
}

function onUpdateBlacklist(list) {
  // Configs atualizadas
}

function onUpdateCategories(rules) {
  // Regras atualizadas
}
</script>

<style scoped>
.config-page-header {
  margin-bottom: 1.5rem;
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

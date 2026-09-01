<template>
  <div class="glass-panel config-panel animate-fade-in" :class="{ 'is-collapsed': isCollapsed }" style="animation-delay: 0.1s;">
    <div class="panel-header" @click="toggleCollapse">
      <h3>
        <Tag :size="18" />
        {{ t('category_manager.title', 'Gerenciador Dinâmico de Categorias') }}
        <span class="badge">{{ t('category_manager.local_sim', 'Simulação Local') }}</span>
      </h3>
      <button class="btn-toggle">
        <component :is="isCollapsed ? ChevronDown : ChevronUp" :size="16" />
        {{ isCollapsed ? t('category_manager.expand', 'Expandir') : t('category_manager.collapse', 'Minimizar') }}
      </button>
    </div>
    
    <transition name="slide-fade">
      <div v-show="!isCollapsed" class="panel-content mt-3">
        <p class="subtitle">{{ t('category_manager.subtitle', 'Associe palavras-chave aos nomes das categorias para organizar os produtos.') }}</p>
        
        <div class="rules-list">
          <div v-for="(rule, index) in rules" :key="index" class="rule-item">
            <span class="text-muted">{{ t('category_manager.if_title_contains', 'Se o título contiver:') }}</span>
            <input type="text" v-model="rule.keyword" :placeholder="t('category_manager.keyword_placeholder', 'ex: noivos')" class="glass-input small" />
            <span class="text-muted text-flex">
              <ArrowRight :size="14" />
              {{ t('category_manager.category_label', 'Categoria:') }}
            </span>
            <input type="text" v-model="rule.category" :placeholder="t('category_manager.category_placeholder', 'ex: Casamento')" class="glass-input small" />
            <button @click="removeRule(index)" class="btn-icon" :title="t('category_manager.remove_rule', 'Remover')">
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
        
        <div class="actions">
          <button @click="addRule" class="btn secondary btn-flex">
            <Plus :size="15" />
            {{ t('category_manager.add_rule', 'Adicionar Regra') }}
          </button>
          <button @click="saveConfigs" class="btn primary btn-flex">
            <Save :size="15" />
            {{ t('category_manager.save_rules', 'Aplicar e Salvar Regras') }}
          </button>
          <span v-if="statusMessage" class="status-msg">{{ statusMessage }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Tag, ChevronDown, ChevronUp, ArrowRight, Trash2, Plus, Save } from 'lucide-vue-next'
import { createClient } from '@supabase/supabase-js'
import { useAppI18n } from '~/composables/useAppI18n'

const { t } = useAppI18n()

const config = useRuntimeConfig()
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseAnonKey)

const props = defineProps({
  user: { type: Object, default: null }
})

const emit = defineEmits(['update-categories'])

const rules = ref([])
const statusMessage = ref('')
const isCollapsed = ref(true)

watch(() => props.user, () => {
  loadConfigs()
})

onMounted(() => {
  const savedState = localStorage.getItem('category_panel_collapsed')
  if (savedState !== null) isCollapsed.value = JSON.parse(savedState)
  loadConfigs()
})

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('category_panel_collapsed', JSON.stringify(isCollapsed.value))
}

async function loadConfigs() {
  if (props.user) {
    const { data, error } = await supabase
      .from('configuracoes_scraper')
      .select('regras_categoria')
      .eq('user_id', props.user.id)
      .single()
      
    if (data && data.regras_categoria && data.regras_categoria.length > 0) {
      rules.value = data.regras_categoria
      emit('update-categories', rules.value)
      return
    }
  }

  // Fallback Local
  const saved = localStorage.getItem('biscuit_category_rules')
  if (saved) {
    rules.value = JSON.parse(saved)
  } else {
    rules.value = [
      { keyword: 'vela', category: 'Velas' },
      { keyword: 'topo', category: 'Topos de Bolo' },
      { keyword: 'bolo', category: 'Topos de Bolo' },
      { keyword: 'chaveiro', category: 'Chaveiros/Lembrancinhas' },
      { keyword: 'lembrancinha', category: 'Chaveiros/Lembrancinhas' }
    ]
  }
  emit('update-categories', rules.value)
}

async function saveConfigs() {
  const validRules = rules.value.filter(r => r.keyword.trim() !== '' && r.category.trim() !== '')
  
  // Cache local
  localStorage.setItem('biscuit_category_rules', JSON.stringify(validRules))
  
  if (props.user) {
    const { error } = await supabase.from('configuracoes_scraper').upsert(
      { user_id: props.user.id, regras_categoria: validRules },
      { onConflict: 'user_id' }
    )
    if (error) {
      showStatus(t('category_manager.error_cloud', 'Erro ao salvar categorias na nuvem!'))
      console.error(error)
      return
    }
    showStatus(t('category_manager.success_cloud', 'Categorias salvas na nuvem!'))
  } else {
    showStatus(t('category_manager.saved_local', 'Regras salvas localmente (Logue para persistir na nuvem)'))
  }
  emit('update-categories', validRules)
}

function showStatus(msg) {
  statusMessage.value = msg
  setTimeout(() => statusMessage.value = '', 3500)
}
function addRule() { rules.value.push({ keyword: '', category: '' }) }
function removeRule(idx) { rules.value.splice(idx, 1) }
</script>

<style scoped>
.config-panel { padding: 1.5rem; margin-bottom: 2rem; transition: padding 0.3s ease; }
.config-panel.is-collapsed { padding: 1rem 1.5rem; margin-bottom: 1rem; }
.panel-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.panel-header h3 { margin: 0; color: var(--text-main); font-size: 1.25rem; display: flex; align-items: center; gap: 0.8rem; }
.badge { font-size: 0.7rem; background: rgba(192, 132, 252, 0.2); color: var(--neon-purple); padding: 0.2rem 0.6rem; border-radius: 99px; border: 1px solid rgba(192, 132, 252, 0.4); text-transform: uppercase; letter-spacing: 0.05em; font-weight: bold; }
.btn-toggle { background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.9rem; font-weight: bold; transition: color 0.2s; outline: none; display: flex; align-items: center; gap: 0.4rem; }
.btn-toggle:hover { color: var(--neon-purple); }

.mt-3 { margin-top: 1.5rem; }
.subtitle { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.2rem; }
.rules-list { display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1.2rem; }
.rule-item { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; background: rgba(0,0,0,0.1); padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid var(--border-glass); }
.text-muted { color: var(--text-muted); font-size: 0.9rem; }
.text-flex { display: flex; align-items: center; gap: 0.3rem; }
.glass-input.small { background: rgba(255,255,255,0.05); border: 1px solid var(--border-glass); color: var(--text-main); padding: 0.4rem 0.8rem; border-radius: 6px; outline: none; transition: border 0.3s; width: 180px; }
.glass-input.small:focus { border-color: var(--neon-purple); }
.btn-icon { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #ef4444; cursor: pointer; padding: 0.4rem 0.6rem; border-radius: 6px; transition: 0.2s; display: flex; align-items: center; justify-content: center; }
.btn-icon:hover { background: rgba(239, 68, 68, 0.3); }
.actions { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.btn-flex { display: flex; align-items: center; gap: 0.4rem; }
.btn { padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn.primary { background: var(--neon-purple); color: #000; }
.btn.primary:hover { background: #b062fb; box-shadow: 0 0 15px rgba(192, 132, 252, 0.4); }
.btn.secondary { background: rgba(255, 255, 255, 0.05); color: var(--text-main); border: 1px solid var(--border-glass); }
.btn.secondary:hover { background: rgba(255, 255, 255, 0.1); }
.status-msg { color: #10b981; font-weight: 600; font-size: 0.9rem; }

/* Transição do Vue */
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; overflow: hidden; transform-origin: top; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; max-height: 0; transform: translateY(-10px); }
.slide-fade-enter-to, .slide-fade-leave-from { opacity: 1; max-height: 1000px; transform: translateY(0); }
</style>

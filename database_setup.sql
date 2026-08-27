-- ==============================================================================
-- 🚀 SUPABASE DATABASE SETUP & MIGRATION: SAAS MULTI-TENANT & RLS
-- ==============================================================================
-- Este script adiciona com segurança as colunas necessárias às tabelas existentes,
-- cria as tabelas que faltarem e aplica as políticas de segurança (RLS).
-- ==============================================================================

-- 1. GARANTE A CRIAÇÃO DAS TABELAS CASO NÃO EXISTAM
CREATE TABLE IF NOT EXISTS public.configuracoes_scraper (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nome_projeto TEXT DEFAULT 'Meu Dashboard de Inteligência',
    nicho_mercado TEXT DEFAULT 'Geral',
    termos_busca JSONB DEFAULT '["biscuit", "vela personalizada"]'::jsonb,
    blacklist JSONB DEFAULT '["molde", "silicone"]'::jsonb,
    regras_categoria JSONB DEFAULT '[]'::jsonb,
    blocked_products JSONB DEFAULT '[]'::jsonb,
    modo_paginacao TEXT DEFAULT 'anonimo',
    status_scraper TEXT,
    status_alerta JSONB,
    relatorio_insights JSONB,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.produtos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plataforma TEXT NOT NULL CHECK (plataforma IN ('meli', 'shopee')),
    id_externo TEXT,
    titulo TEXT NOT NULL,
    link TEXT NOT NULL,
    vendedor TEXT,
    categoria_ia TEXT,
    silenciado BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.historico_coletas (
    id BIGSERIAL PRIMARY KEY,
    produto_id UUID NOT NULL REFERENCES public.produtos(id) ON DELETE CASCADE,
    preco NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    vendas_totais INTEGER NOT NULL DEFAULT 0,
    data_coleta DATE NOT NULL DEFAULT CURRENT_DATE
);

-- 2. MIGRAÇÕES SEGURAS (ADICIONA COLUNAS CASO AS TABELAS JÁ EXISTISSEM)
ALTER TABLE public.produtos 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE public.configuracoes_scraper 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE public.configuracoes_scraper 
ADD COLUMN IF NOT EXISTS status_alerta JSONB;

ALTER TABLE public.configuracoes_scraper 
ADD COLUMN IF NOT EXISTS relatorio_insights JSONB;

-- 3. ÍNDICES DE ALTA PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_produtos_user_id ON public.produtos(user_id);
CREATE INDEX IF NOT EXISTS idx_produtos_plataforma ON public.produtos(plataforma);
CREATE INDEX IF NOT EXISTS idx_produtos_id_externo ON public.produtos(id_externo);
CREATE INDEX IF NOT EXISTS idx_historico_produto_data ON public.historico_coletas(produto_id, data_coleta DESC);

-- ==============================================================================
-- 🔒 POLÍTICAS DE SEGURANÇA ROW LEVEL SECURITY (RLS)
-- ==============================================================================

-- Habilita RLS em todas as tabelas
ALTER TABLE public.configuracoes_scraper ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historico_coletas ENABLE ROW LEVEL SECURITY;

-- 🛡️ POLÍTICA 1: `configuracoes_scraper`
DROP POLICY IF EXISTS "Tenant acessa apenas suas configuracoes" ON public.configuracoes_scraper;
CREATE POLICY "Tenant acessa apenas suas configuracoes"
ON public.configuracoes_scraper
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 🛡️ POLÍTICA 2: `produtos`
DROP POLICY IF EXISTS "Tenant acessa apenas seus proprios produtos" ON public.produtos;
CREATE POLICY "Tenant acessa apenas seus proprios produtos"
ON public.produtos
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 🛡️ POLÍTICA 3: `historico_coletas` (Baseado no produto_id pertencente ao user_id)
DROP POLICY IF EXISTS "Tenant acessa historico dos seus proprios produtos" ON public.historico_coletas;
CREATE POLICY "Tenant acessa historico dos seus proprios produtos"
ON public.historico_coletas
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM public.produtos
        WHERE public.produtos.id = public.historico_coletas.produto_id
        AND public.produtos.user_id = auth.uid()
    )
);

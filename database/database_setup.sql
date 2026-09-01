-- ==============================================================================
-- 🍪 BISCUIT SCRAPER: SETUP DO BANCO DE DADOS (SUPABASE / POSTGRESQL)
-- ==============================================================================
-- Este script cria as tabelas essenciais para armazenar as configurações de busca,
-- os anúncios de produtos minerados e o histórico diário de preços e vendas.
-- ==============================================================================

-- 1. TABELA DE CONFIGURAÇÕES DO SCRAPER E TERMOS
CREATE TABLE IF NOT EXISTS public.configuracoes_scraper (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_projeto TEXT DEFAULT 'BiscuitInsights',
    termos_busca JSONB DEFAULT '["topo de bolo biscuit", "vela biscuit", "lembrancinha biscuit", "chaveiro biscuit"]'::jsonb,
    blacklist JSONB DEFAULT '["molde", "silicone", "esteca", "papel"]'::jsonb,
    regras_categoria JSONB DEFAULT '[]'::jsonb,
    blocked_products JSONB DEFAULT '[]'::jsonb,
    modo_paginacao TEXT DEFAULT 'anonimo',
    disparo_pendente BOOLEAN DEFAULT FALSE,
    status_scraper TEXT,
    status_alerta JSONB,
    relatorio_insights JSONB,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TABELA DE PRODUTOS COLETADOS
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

-- 3. TABELA DE HISTÓRICO DE COLETAS (PREÇOS E VENDAS DIÁRIAS)
CREATE TABLE IF NOT EXISTS public.historico_coletas (
    id BIGSERIAL PRIMARY KEY,
    produto_id UUID NOT NULL REFERENCES public.produtos(id) ON DELETE CASCADE,
    preco NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    vendas_totais INTEGER NOT NULL DEFAULT 0,
    data_coleta DATE NOT NULL DEFAULT CURRENT_DATE
);

-- 4. ÍNDICES DE PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_produtos_plataforma ON public.produtos(plataforma);
CREATE INDEX IF NOT EXISTS idx_produtos_id_externo ON public.produtos(id_externo);
CREATE INDEX IF NOT EXISTS idx_historico_produto_data ON public.historico_coletas(produto_id, data_coleta DESC);

-- 5. POLÍTICAS DE ACESSO (PERMITE LEITURA E ESCRITA VIA API/ANON KEY)
ALTER TABLE public.configuracoes_scraper ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historico_coletas ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Acesso publico configuracoes" ON public.configuracoes_scraper;
CREATE POLICY "Acesso publico configuracoes" ON public.configuracoes_scraper FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Acesso publico produtos" ON public.produtos;
CREATE POLICY "Acesso publico produtos" ON public.produtos FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Acesso publico historico" ON public.historico_coletas;
CREATE POLICY "Acesso publico historico" ON public.historico_coletas FOR ALL USING (true) WITH CHECK (true);

-- 6. INSERE CONFIGURAÇÃO INICIAL SE A TABELA ESTIVER VAZIA
INSERT INTO public.configuracoes_scraper (nome_projeto, status_scraper)
SELECT 'BiscuitInsights', '🟢 Sistema pronto para monitoramento.'
WHERE NOT EXISTS (SELECT 1 FROM public.configuracoes_scraper);

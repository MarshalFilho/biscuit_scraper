### 🗺️ Plano de Execução: Scraper Serverless com Histórico

#### Etapa 1: Modelagem do Banco de Dados (Supabase / PostgreSQL)

Vamos criar uma estrutura relacional simples, mas poderosa, separando o que é o "Produto" do que é a "Foto do momento" (Histórico).

**Tabela 1: `produtos**` (Guarda informações que não mudam com o tempo)

- `id` (UUID, Chave Primária)
- `plataforma` (String: 'meli', 'shopee', 'elo7')
- `id_externo` (String: O código do anúncio na plataforma, ex: 'MLB123456')
- `titulo` (String: O nome do anúncio)
- `link` (String: URL do produto)
- `categoria_ia` (String: Campo que será preenchido depois pela IA)
- `criado_em` (Timestamp: Quando o robô achou esse produto pela primeira vez)

**Tabela 2: `historico_coletas**` (A "Máquina do Tempo" - Recebe novos registros toda semana)

- `id` (UUID, Chave Primária)
- `produto_id` (UUID, Chave Estrangeira apontando para a tabela `produtos`)
- `preco` (Decimal: Preço no dia da coleta)
- `vendas_totais` (Inteiro: Quantidade de vendas registradas no dia)
- `data_coleta` (Date: A data em que o script rodou)

> **💡 Exemplo de Consulta Semanal (SQL explícito):**
> Quando quisermos ver a evolução, faremos uma query cruzando os dados sem usar atalhos:
>
> ```sql
> SELECT
>     produtos.titulo,
>     historico_coletas.preco,
>     historico_coletas.vendas_totais,
>     historico_coletas.data_coleta
> FROM produtos
> INNER JOIN historico_coletas ON produtos.id = historico_coletas.produto_id
> WHERE produtos.id_externo = 'MLB123456'
> ORDER BY historico_coletas.data_coleta ASC;
>
> ```

---

#### Etapa 2: Refatoração do Scraper Python

Precisamos alterar a forma como a sua "Camada Ouro" funciona no `src/main.py`. Em vez de gerar um JSON e um Excel localmente, o Python vai enviar os dados para a nuvem.

**Novas Funções a implementar:**

1. **`conectar_supabase()`**: Inicializa o cliente do Supabase usando variáveis de ambiente (para esconder suas senhas).
2. **`upsert_produto(dados_produto)`**: Verifica no banco se o `id_externo` (ex: o código do anúncio) já existe. Se não existir, cadastra na tabela `produtos`. Se já existir, apenas retorna o `id` interno do banco.
3. **`registrar_historico(produto_id, preco, vendas)`**: Pega o `id` do produto e insere uma linha nova na tabela `historico_coletas` com a data do dia.

---

#### Etapa 3: Automação na Nuvem (GitHub Actions)

Aqui é onde a mágica do custo zero acontece. Vamos criar um arquivo dentro do seu repositório em `.github/workflows/scraper_semanal.yml`.

**O que esse arquivo fará:**

- Terá um gatilho de _cron job_ (ex: `cron: '0 3 * * 1'` -> Roda toda segunda-feira às 03:00 da manhã).
- Instalará o Python e o Playwright na máquina virtual do GitHub.
- Injetará as credenciais do Supabase de forma segura (usando o _GitHub Secrets_).
- Executará o seu comando `python src/main.py --plataforma meli`.

---

#### Etapa 4: O Novo Dashboard (GitHub Pages)

Como abandonaremos o Streamlit para poder hospedar gratuitamente no GitHub Pages, precisaremos de um front-end focado em consumir arquivos estáticos ou APIs.

Para o front-end estático no GitHub Pages, uma abordagem excelente e escalável é gerar arquivos estáticos utilizando o ecossistema JavaScript/TypeScript. Um projeto configurado com **Vue.js ou Nuxt** gera pacotes estáticos perfeitos para esse cenário. O site carregará no navegador do usuário e o próprio código JavaScript (Client-Side) fará a requisição HTTP diretamente para a API REST automática que o Supabase já fornece gratuitamente, montando os gráficos na tela.

**Novos Gráficos (Baseados no Histórico):**

- **Linha do Tempo de Preço:** Como o preço médio do nicho flutuou no último mês.
- **Top Crescimento:** Uma tabela mostrando `(Vendas Hoje) - (Vendas Semana Passada)` para identificar os produtos que estão "bombando" agora.

---

#### Etapa 5: Enriquecimento Subjetivo (IA Integrada)

Uma vez que os dados estejam caindo no banco redondinhos toda semana, adicionamos um passo final no seu script Python.

- A IA (OpenAI/Gemini) vai ler os títulos recém-adicionados no banco.
- Vai classificar o produto e salvar o resultado no campo `categoria_ia` da tabela `produtos`.
- _Exemplo:_ O seu Dashboard passará a ter um filtro: _"Mostrar apenas matérias-primas"_ ou _"Mostrar apenas produtos finalizados"_, tudo inferido automaticamente pela IA.

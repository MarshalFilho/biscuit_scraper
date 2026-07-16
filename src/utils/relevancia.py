import unicodedata
import re
import config

def normalizar_texto(texto):
    """
    Normaliza o texto removendo acentos e convertendo para minúsculas.
    """
    if not texto: return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.lower()

def verificar_relevancia(titulo, termo_busca):
    """
    Verifica se o título do anúncio é relevante baseado no termo de busca
    e nas regras configuradas no Supabase.
    """
    titulo_norm = normalizar_texto(titulo)
    termo_norm = normalizar_texto(termo_busca)
    
    # 1. Regra Global Obrigatória
    obrigatoria = config.get_palavra_obrigatoria_global()
    if obrigatoria:
        if normalizar_texto(obrigatoria) not in titulo_norm:
            return False
            
    # 2. Palavras Negativas (parcial)
    for neg in config.get_blacklist():
        if normalizar_texto(neg) in titulo_norm:
            return False
            
    # 3. Palavras Negativas Exatas
    palavras = re.split(r'\W+', titulo_norm)
    for neg_exata in config.get_palavras_negativas_exatas():
        if normalizar_texto(neg_exata) in palavras:
            return False
            
    # 4. Regras de Tipo de Produto
    for tipo, keywords in config.get_regras_tipo_produto().items():
        if normalizar_texto(tipo) in termo_norm:
            keywords_norm = [normalizar_texto(k) for k in keywords]
            if not any(k in titulo_norm for k in keywords_norm):
                return False
                
    # 5. Regras de Conteúdo/Tema
    for tema, keywords in config.get_regras_conteudo_busca().items():
        if normalizar_texto(tema) in termo_norm:
            keywords_norm = [normalizar_texto(k) for k in keywords]
            has_match = False
            for k in keywords_norm:
                if k in ["pet", "vet"]:
                    if k in palavras:
                        has_match = True
                        break
                else:
                    if k in titulo_norm:
                        has_match = True
                        break
            if not has_match:
                return False
                
    # 6. Regra de Associação com o Termo de Busca
    palavras_busca = [normalizar_texto(w) for w in termo_busca.split() if len(w) > 2]
    has_search_term_match = False
    for pb in palavras_busca:
        # Mantendo retrocompatibilidade com 'biscuit' para o caso de nichos genéricos legados
        if pb == "biscuit":
            if "biscui" in titulo_norm:
                has_search_term_match = True
                break
        else:
            if pb in titulo_norm:
                has_search_term_match = True
                break
                
    if not has_search_term_match:
        return False
        
    # 7. Salvaguarda para Termos Sem Tema
    tem_tema = False
    for tema in config.get_regras_conteudo_busca().keys():
        if normalizar_texto(tema) in termo_norm:
            tem_tema = True
            break
            
    if not tem_tema and "biscui" not in titulo_norm:
        return False
        
    return True

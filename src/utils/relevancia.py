import unicodedata
import re
from config import (
    PALAVRA_OBRIGATORIA_GLOBAL,
    PALAVRAS_NEGATIVAS,
    PALAVRAS_NEGATIVAS_EXATAS,
    REGRAS_TIPO_PRODUTO,
    REGRAS_CONTEUDO_BUSCA
)

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
    e nas regras configuradas no config.py.
    """
    titulo_norm = normalizar_texto(titulo)
    termo_norm = normalizar_texto(termo_busca)
    
    # 1. Regra Global Obrigatória
    if PALAVRA_OBRIGATORIA_GLOBAL:
        if normalizar_texto(PALAVRA_OBRIGATORIA_GLOBAL) not in titulo_norm:
            return False
            
    # 2. Palavras Negativas (parcial)
    for neg in PALAVRAS_NEGATIVAS:
        if normalizar_texto(neg) in titulo_norm:
            return False
            
    # 3. Palavras Negativas Exatas
    palavras = re.split(r'\W+', titulo_norm)
    for neg_exata in PALAVRAS_NEGATIVAS_EXATAS:
        if normalizar_texto(neg_exata) in palavras:
            return False
            
    # 4. Regras de Tipo de Produto
    for tipo, keywords in REGRAS_TIPO_PRODUTO.items():
        if normalizar_texto(tipo) in termo_norm:
            keywords_norm = [normalizar_texto(k) for k in keywords]
            # Se o termo contém a chave do tipo, DEVE ter pelo menos um dos keywords no título
            if not any(k in titulo_norm for k in keywords_norm):
                return False
                
    # 5. Regras de Conteúdo/Tema (ex: órgãos, animais)
    for tema, keywords in REGRAS_CONTEUDO_BUSCA.items():
        if normalizar_texto(tema) in termo_norm:
            keywords_norm = [normalizar_texto(k) for k in keywords]
            has_match = False
            for k in keywords_norm:
                # Regra especial para palavras curtas onde queremos correspondência exata
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
    # O título deve conter pelo menos uma das palavras significativas da busca original.
    palavras_busca = [normalizar_texto(w) for w in termo_busca.split() if len(w) > 2]
    has_search_term_match = False
    for pb in palavras_busca:
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
    # Se a busca não corresponder a nenhum tema específico (rim, coração, pet, etc.),
    # o anúncio deve obrigatoriamente conter a palavra 'biscui' no título para evitar
    # livros, brinquedos de plástico e louças sanitárias de cor "biscuit".
    tem_tema = False
    for tema in REGRAS_CONTEUDO_BUSCA.keys():
        if normalizar_texto(tema) in termo_norm:
            tem_tema = True
            break
            
    if not tem_tema and "biscui" not in titulo_norm:
        return False
        
    return True

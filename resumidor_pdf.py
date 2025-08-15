from pdfminer.high_level import extract_text
import spacy
from collections import Counter
import re
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _load_nlp() -> spacy.language.Language:
    """
    Tenta carregar o modelo de linguagem em Português. 
    Se falhar, retorna um pipeline mínimo com sentencizer.
    
    Returns:
        spacy.language.Language: O modelo de linguagem carregado.
    """
    try:
        return spacy.load('pt_core_news_sm')
    except Exception as e:
        logging.warning(f"Falha ao carregar o modelo de linguagem: {e}. Usando pipeline mínimo.")
        nlp = spacy.blank('pt')
        if 'sentencizer' not in nlp.pipe_names:
            nlp.add_pipe('sentencizer')
        return nlp

nlp = _load_nlp()

def limpar_texto(texto: str) -> str:
    """
    Remove quebras de linha e espaços em branco extras do texto.
    """
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def ler_pdf(caminho_pdf: str) -> str:
    """
    Lê o conteúdo de um arquivo PDF e retorna o texto limpo.
    """
    try:
        texto = extract_text(caminho_pdf) or ''
        return limpar_texto(texto)  # Limpa o texto extraído
    except Exception as e:
        logging.error(f"Erro ao ler PDF: {e}")
        return ''

def resumir_com_spacy(texto: str, num_sentencas: int = 3) -> str:
    """
    Resume o texto usando spaCy com melhorias:
    - Lematização das palavras
    - Ignora frases curtas
    - Número de frases proporcional ao tamanho do texto
    - Remove redundância entre frases
    """
    if not texto.strip():
        logging.warning("Texto vazio fornecido para resumo.")
        return ''
    
    doc = nlp(texto)
    sentencas = list(doc.sents)

    if not sentencas:
        logging.warning("Nenhuma sentença encontrada no texto.")
        return texto.strip()[:1000]

    # Ajusta dinamicamente o número de frases (mínimo 3)
    num_sentencas = max(num_sentencas, len(sentencas) // 10)

    # Tokenização com lematização
    palavras = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]
    frequencia = Counter(palavras)

    # Calcula peso das sentenças (ignora frases muito curtas)
    sentencas_com_peso = [
        (sum(frequencia.get(t.lemma_.lower(), 0) for t in s if t.is_alpha), s.text.strip())
        for s in sentencas if len(s.text.strip().split()) > 5
    ]

    if not sentencas_com_peso:
        logging.warning("Não foi possível calcular pesos. Retornando primeiras frases.")
        return ' '.join(s.text.strip() for s in sentencas[:num_sentencas])

    # Ordena pelo peso
    melhores = sorted(sentencas_com_peso, key=lambda x: x[0], reverse=True)
    
    # Remove redundância (similaridade alta)
    resumo_frases = []
    for _, frase in melhores:
        if all(nlp(frase).similarity(nlp(f)) < 0.85 for f in resumo_frases):
            resumo_frases.append(frase)
        if len(resumo_frases) >= num_sentencas:
            break

    return ' '.join(resumo_frases)

# Exemplo de uso (para testar o script diretamente)
if __name__ == '__main__':
    caminho_do_pdf = 'documento_teste.pdf'
    texto_extraido = ler_pdf(caminho_do_pdf)
    resumo = resumir_com_spacy(texto_extraido, num_sentencas=3)
    
    print("\n--- Resumo Gerado ---")
    print(resumo)

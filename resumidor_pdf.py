from pdfminer.high_level import extract_text
import spacy
from collections import Counter
import re
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def _load_nlp() -> spacy.language.Language:
    """
    Tenta carregar o modelo de linguagem em Português.
    Se falhar, cria um pipeline mínimo com sentencizer.
    """
    try:
        return spacy.load("pt_core_news_sm")
    except Exception as e:
        logging.warning(f"Falha ao carregar modelo spaCy: {e}. Usando pipeline mínimo.")
        nlp = spacy.blank("pt")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp

nlp = _load_nlp()

def limpar_texto(texto: str) -> str:
    if not texto:
        return ""
    # remove bullets, símbolos, traços
    texto = re.sub(r'[•◦●▪◆►–—\-]+', ' ', texto)
    texto = re.sub(r'[(){}\[\]·]', ' ', texto)
    texto = re.sub(r'[_=]+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)  # colapsa espaços
    texto = re.sub(r'\b\d+\b', '', texto)  # remove números soltos
    return texto.strip()

def ler_pdf(caminho_pdf: str) -> str:
    """
    Extrai texto de um PDF e aplica limpeza básica.
    """
    try:
        texto = extract_text(caminho_pdf) or ""
        return limpar_texto(texto)
    except Exception as e:
        logging.error(f"Erro ao ler PDF: {e}")
        return ""

def _frase_informativa(frase: str) -> bool:
    """
    Filtra frases que provavelmente não agregam valor ao resumo:
    - Muito curtas (menos de 8 palavras)
    - Cabeçalhos em CAIXA ALTA
    """
    palavras = frase.split()
    if len(palavras) < 8:
        return False
    if frase.isupper():
        return False
    return True

def resumir_com_spacy(texto: str, num_sentencas: int = 5) -> str:
    if not texto.strip():
        logging.warning("Texto vazio fornecido para resumo.")
        return ""

    # Limpeza extra para remover símbolos estranhos
    texto = re.sub(r'[•◦●▪◆►–—\-]+', ' ', texto)  # substitui marcadores
    texto = re.sub(r'[_=]+', ' ', texto)  # linhas horizontais
    texto = re.sub(r'\s+', ' ', texto)  # espaços extras

    doc = nlp(texto)
    sentencas = [s.text.strip() for s in doc.sents if _frase_informativa(s.text.strip())]

    if not sentencas:
        logging.warning("Nenhuma sentença válida encontrada.")
        return texto.strip()[:500]

    dinamico = max(3, min(8, len(sentencas) // 10))
    num_sentencas = max(num_sentencas, dinamico)

    palavras = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]
    frequencia = Counter(palavras)

    keywords = {"scrum", "sprint", "product", "owner", "backlog", "ágil", "agile", "metodologia", "artefato", "cerimônia"}
    for kw in keywords:
        frequencia[kw] += 3

    sentencas_com_peso = [
        (sum(frequencia.get(t.lemma_.lower(), 0) for t in nlp(s) if t.is_alpha), s)
        for s in sentencas
    ]

    melhores = sorted(sentencas_com_peso, key=lambda x: x[0], reverse=True)

    resumo_frases = []
    for _, frase in melhores:
        frase = frase.strip()

        # Corta frases muito longas em pedaços menores
        if len(frase.split()) > 25:
            partes = re.split(r'(?<=[.!?])\s+', frase)
            frase = partes[0]  # pega só a primeira parte

        # Descarta frases redundantes
        tokens = set(frase.lower().split())
        if all(len(tokens & set(f.lower().split())) / max(1, len(tokens)) < 0.5 for f in resumo_frases):
            resumo_frases.append(frase)
        if len(resumo_frases) >= num_sentencas:
            break

    resumo_frases = sorted(resumo_frases, key=lambda f: sentencas.index(f))

    # Formata como tópicos
    resumo_final = "\n".join([f"• {fr}" for fr in resumo_frases if fr])
    return resumo_final


# Teste rápido no terminal
if __name__ == "__main__":
    caminho = "documento_teste.pdf"
    texto = ler_pdf(caminho)
    resumo = resumir_com_spacy(texto, num_sentencas=5)
    print("\n--- Resumo Gerado ---\n")
    print(resumo)

from pdfminer.high_level import extract_text
import spacy
from collections import Counter
import re
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def _load_nlp() -> spacy.language.Language:
    """Carrega o modelo em português ou usa pipeline mínimo."""
    try:
        return spacy.load("pt_core_news_sm")
    except Exception as e:
        logging.warning(f"Falha ao carregar spaCy: {e}. Usando pipeline mínimo.")
        nlp = spacy.blank("pt")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp

nlp = _load_nlp()

def limpar_texto(texto: str) -> str:
    """
    Limpa o texto extraído do PDF:
    - Remove quebras de linha
    - Remove números soltos (ex: páginas, ISBN)
    - Remove bullets e caracteres especiais
    """
    if not texto:
        return ""
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"\b\d+\b", "", texto)
    texto = re.sub(r"(ISBN|CIP|Catalogação|Orientador|Orientadora|Conselho Editorial).*", "", texto, flags=re.I)
    texto = texto.replace("•", "").replace("◦", "")
    return texto.strip()

def ler_pdf(caminho_pdf: str) -> str:
    """Extrai texto de um PDF e aplica limpeza básica."""
    try:
        texto = extract_text(caminho_pdf) or ""
        return limpar_texto(texto)
    except Exception as e:
        logging.error(f"Erro ao ler PDF: {e}")
        return ""

def _frase_informativa(frase: str) -> bool:
    """
    Mantém apenas frases que parecem narrativas relevantes:
    - Pelo menos 5 palavras
    - Não toda em maiúscula
    - Ignora se conter palavras de autoria/ficha técnica
    """
    if len(frase.split()) < 5:
        return False
    if frase.isupper():
        return False
    blacklist = ["autor", "orientador", "secretaria", "universidade", "catalogação", "editorial"]
    if any(palavra.lower() in frase.lower() for palavra in blacklist):
        return False
    return True

def resumir_com_spacy(texto: str, num_sentencas: int = 3) -> str:
    """
    Resume o texto:
    - Filtra frases irrelevantes
    - Ordena por peso (frequência de palavras)
    - Retorna resumo curto e objetivo
    """
    if not texto.strip():
        return ""

    doc = nlp(texto)
    sentencas = [s.text.strip() for s in doc.sents if _frase_informativa(s.text.strip())]

    if not sentencas:
        return texto.strip()[:400]

    # Reduz dinamicamente o tamanho: mínimo 2, máximo 5 frases
    num_sentencas = max(2, min(5, num_sentencas))

    # Frequência de palavras
    palavras = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]
    frequencia = Counter(palavras)

    # Calcula peso das sentenças
    sentencas_com_peso = [
        (sum(frequencia.get(t.lemma_.lower(), 0) for t in nlp(s) if t.is_alpha), s)
        for s in sentencas
    ]

    melhores = sorted(sentencas_com_peso, key=lambda x: x[0], reverse=True)

    resumo_frases = []
    usados = set()
    for _, frase in melhores:
        tokens = set(frase.lower().split())
        if all(len(tokens & set(f.lower().split())) / max(1, len(tokens)) < 0.6 for f in resumo_frases):
            resumo_frases.append(frase)
        if len(resumo_frases) >= num_sentencas:
            break

    resumo_frases = sorted(resumo_frases, key=lambda f: sentencas.index(f))

    return " ".join(resumo_frases)

# Teste rápido
if __name__ == "__main__":
    caminho = "documento_teste.pdf"
    texto = ler_pdf(caminho)
    resumo = resumir_com_spacy(texto, num_sentencas=3)
    print("\n--- Resumo Gerado ---\n")
    print(resumo)

from pdfminer.high_level import extract_text
import spacy
from collections import Counter

# Tenta carregar o modelo de Português; faz fallback para um pipeline mínimo
def _load_nlp():
    try:
        return spacy.load('pt_core_news_sm')
    except Exception:
        nlp = spacy.blank('pt')
        if 'sentencizer' not in nlp.pipe_names:
            nlp.add_pipe('sentencizer')
        return nlp

nlp = _load_nlp()

def ler_pdf(caminho_pdf: str) -> str:
    try:
        return extract_text(caminho_pdf) or ''
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return ''

def resumir_com_spacy(texto: str, num_sentencas: int = 3) -> str:
    if not texto.strip():
        return ''
    doc = nlp(texto)
    palavras = [t.text.lower() for t in doc if t.is_alpha and not t.is_stop]
    if not palavras:
        # Se não conseguir tokenizar, devolve primeiras frases
        sents = [s.text.strip() for s in doc.sents]
        return ' '.join(sents[:num_sentencas])

    from collections import Counter
    frequencia = Counter(palavras)
    sentencas = list(doc.sents)
    if not sentencas:
        return texto.strip()[:1000]

    sentencas_com_peso = [
        (sum(frequencia.get(t.text.lower(), 0) for t in s if t.is_alpha), s.text.strip())
        for s in sentencas
    ]
    melhores = sorted(sentencas_com_peso, key=lambda x: x[0], reverse=True)[:num_sentencas]
    return ' '.join(s[1] for s in melhores)

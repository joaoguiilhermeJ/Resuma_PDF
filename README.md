# Resuma PDF

Aplicação web em **Flask** que permite o upload de arquivos PDF e gera um **resumo automático em português** usando **spaCy** e **PDFMiner**.

## Funcionalidades
- Upload de arquivos PDF arrastando ou selecionando no navegador
- Extração automática de texto com **pdfminer.six**
- Limpeza e normalização do texto
- Resumo inteligente com **spaCy**
- Resultado exibido em tela, com opção de:
  - Copiar texto
  - Baixar resumo em `.txt`
- Deploy pronto para **Render** ou outro serviço compatível

---

## Demonstração
![Tela inicial](static/preview.png)  
> Exemplo da tela de upload (adicione prints do seu sistema).

---

## Tecnologias utilizadas
- [Flask](https://flask.palletsprojects.com/) - Backend e rotas
- [pdfminer.six](https://github.com/pdfminer/pdfminer.six) - Extração de texto de PDFs
- [spaCy](https://spacy.io/) - NLP para resumo
- [gunicorn](https://gunicorn.org/) - Servidor WSGI para produção
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Variáveis de ambiente

---

## Instalação local

1. Clone o repositório:
   ```bash
   git clone https://github.com/joaoguiilhermeJ/Resuma_PDF.git
   cd Resuma_PDF

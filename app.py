
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from resumidor_pdf import ler_pdf, resumir_com_spacy
import os, uuid

# Carrega variáveis do .env se existir
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf'}

def allowed_file(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/resumir", methods=["POST"])
def resumir():
    if "arquivo" not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado"}), 400

    arquivo = request.files["arquivo"]
    if not arquivo or arquivo.filename == '':
        return jsonify({"erro": "Nenhum arquivo selecionado"}), 400

    if not allowed_file(arquivo.filename):
        return jsonify({"erro": "Formato inválido. Envie um PDF."}), 400

    nome_arquivo = f"{uuid.uuid4()}_{arquivo.filename}"
    caminho_pdf = os.path.join(UPLOAD_FOLDER, nome_arquivo)
    arquivo.save(caminho_pdf)

    try:
        texto = ler_pdf(caminho_pdf)
        if not texto.strip():
            return jsonify({"erro": "Não foi possível extrair texto do PDF"}), 400

        # Obter o número de sentenças do corpo da requisição
        num_sentencas = int(request.form.get("num_sentencas", 3))  # Padrão para 3
        resumo = resumir_com_spacy(texto, num_sentencas=num_sentencas)
        resumo = ' '.join(resumo.split())
        session['resumo'] = resumo
        return jsonify({"redirect": url_for('resumo')})
    finally:
        # Limpa o arquivo do servidor após o processamento
        try:
            os.remove(caminho_pdf)
        except Exception:
            pass

@app.route("/resumo")
def resumo():
    resumo = session.get('resumo', '')
    return render_template("resumo.html", resumo=resumo)

if __name__ == "__main__":
    app.run(debug=True)

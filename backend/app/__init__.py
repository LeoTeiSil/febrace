from flask import Flask, request, jsonify
from flask_cors import CORS
from app.api import api_bp
import json as _json
import re as _re


def create_app():
    app = Flask(__name__)

    # ===============================
    # INICIALIZAR RAG
    # ===============================
    from .rag import criar_chain_rag

    qa_chain = criar_chain_rag()

    if not qa_chain:
        raise RuntimeError(
            "Falha ao inicializar RAG. Execute python vetorizador.py primeiro!"
        )

    print("Sistema RAG carregado com sucesso!")

    # ===============================
    # CONFIGURACOES
    # ===============================
    CORS(app)
    app.register_blueprint(api_bp)

    # ===============================
    # ROTA INFORMACOES DE DOENCA
    # ===============================
    @app.route("/doenca/<string:nome>", methods=["GET"])
    def info_doenca(nome: str):
        try:
            pergunta = (
                f"Forneça informações detalhadas sobre a doença '{nome}'. "
                "Responda APENAS com um objeto JSON (sem texto adicional, sem markdown) com os campos: "
                "descricao (string explicando a doença), "
                "sintomas (array de strings com os principais sintomas), "
                "tratamentos (array de strings com os principais tratamentos), "
                "aviso (string com aviso médico ao paciente)."
            )

            resultado = qa_chain.invoke({"input": pergunta})

            texto = None
            if isinstance(resultado, dict):
                texto = resultado.get("answer") or resultado.get("result", "")
            else:
                texto = str(resultado)

            # Tenta extrair JSON embutido na resposta do LLM
            match = _re.search(r"\{[\s\S]*\}", texto or "")
            if match:
                try:
                    dados = _json.loads(match.group())
                except _json.JSONDecodeError:
                    dados = None
            else:
                dados = None

            if not dados:
                dados = {
                    "descricao": texto or "Informacao nao disponivel.",
                    "sintomas": [],
                    "tratamentos": [],
                    "aviso": "Consulte um medico para diagnostico correto."
                }

            return jsonify(dados)

        except Exception as e:
            print(f"Erro em /doenca/{nome}: {e}")
            return jsonify({"error": "Erro interno no processamento"}), 500

    # ===============================
    # ROTA RAG
    # ===============================
    @app.route("/perguntar", methods=["POST"])
    def fazer_pergunta():
        data = request.get_json()
        pergunta = data.get("pergunta", "")

        if not pergunta:
            return jsonify({"error": "Forneca uma pergunta"}), 400

        try:
            print(f"Pergunta recebida: {pergunta}")

            resultado = qa_chain.invoke({"input": pergunta})

            resposta = None
            if isinstance(resultado, dict):
                resposta = resultado.get("answer") or resultado.get("result", "")
            else:
                resposta = str(resultado)

            response = {
                "resposta": resposta,
            }

            print(f"Resposta enviada: {len(response['resposta'])} caracteres")

            return jsonify(response)

        except Exception as e:
            print(f"Erro: {e}")
            return jsonify({"error": "Erro interno no processamento"}), 500

    return app

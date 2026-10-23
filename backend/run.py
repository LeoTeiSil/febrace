from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.api.services.services import gerarRespostasLLM
from app.config import DATABASE_URL

from langchain_groq import ChatGroq
from dotenv import load_dotenv

import json, re, os, random

load_dotenv()

# =========================
# CONFIGURAÇÕES
# =========================

app = Flask(__name__)
bcrypt = Bcrypt(app)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET","POST","PUT","DELETE","OPTIONS"]
)

# =========================
# BANCO DE DADOS
# =========================

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# =========================
# HOME
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "API DrAignostico rodando",
        "rotas": [
            "/cadastro (POST)",
            "/login (POST)",
            "/recuperar-senha (POST)",
            "/respostas-llm (POST)",
            "/doenca/<nome> (GET)"
        ]
    })

# =========================
# CADASTRO
# =========================

@app.route("/cadastro", methods=["POST"])
def cadastro():

    try:

        data = request.get_json() or {}

        nome = data.get("nome")
        email = data.get("email")
        senha = data.get("senha")
        crm = data.get("crm")

        if not nome or not email or not senha:
            return jsonify({"erro": "Campos obrigatórios"}), 400

        db = SessionLocal()

        # verificar email duplicado
        check = text("SELECT id FROM usuarios WHERE email = :email")
        existe = db.execute(check, {"email": email}).fetchone()

        if existe:
            db.close()
            return jsonify({"erro": "Email já cadastrado"}), 400

        senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

        query = text("""
        INSERT INTO usuarios (nome, email, senha, crm)
        VALUES (:nome, :email, :senha, :crm)
        """)

        db.execute(query,{
            "nome": nome,
            "email": email,
            "senha": senha_hash,
            "crm": crm
        })

        db.commit()
        db.close()

        return jsonify({
            "status": "usuario criado",
            "email": email
        }), 201

    except Exception as e:
        print("ERRO CADASTRO:", e)
        return jsonify({"erro": str(e)}), 500


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json() or {}

        email = data.get("email")
        senha = data.get("senha")

        db = SessionLocal()

        query = text("SELECT * FROM usuarios WHERE email = :email")

        usuario = db.execute(query, {"email": email}).fetchone()

        db.close()

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        senha_valida = bcrypt.check_password_hash(usuario.senha, senha)

        if not senha_valida:
            return jsonify({"erro": "Senha incorreta"}), 401

        return jsonify({
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        })

    except Exception as e:
        print("ERRO LOGIN:", e)
        return jsonify({"erro": str(e)}), 500


# =========================
# RECUPERAR SENHA
# =========================

@app.route("/recuperar-senha", methods=["POST"])
def recuperar_senha():

    try:

        data = request.get_json() or {}

        crm = data.get("crm")
        email = data.get("email")

        if not crm or not email:
            return jsonify({"erro": "CRM e email são obrigatórios"}), 400

        db = SessionLocal()

        query = text("""
        SELECT * FROM usuarios
        WHERE email = :email AND crm = :crm
        """)

        usuario = db.execute(query,{
            "email": email,
            "crm": crm
        }).fetchone()

        if not usuario:
            db.close()
            return jsonify({"erro": "Usuário não encontrado"}), 404

        nova_senha = str(random.randint(100000, 999999))

        senha_hash = bcrypt.generate_password_hash(nova_senha).decode("utf-8")

        update = text("""
        UPDATE usuarios
        SET senha = :senha
        WHERE id = :id
        """)

        db.execute(update,{
            "senha": senha_hash,
            "id": usuario.id
        })

        db.commit()
        db.close()

        return jsonify({
            "status": "Senha redefinida",
            "nova_senha": nova_senha
        })

    except Exception as e:
        print("ERRO RECUPERAR SENHA:", e)
        return jsonify({"erro": str(e)}), 500


# =========================
# PERFIL
# =========================

@app.route("/usuario/<int:id>", methods=["GET"])
def get_usuario(id):

    try:

        db = SessionLocal()

        query = text("""
        SELECT id, nome, email, crm
        FROM usuarios
        WHERE id = :id
        """)

        usuario = db.execute(query, {"id": id}).fetchone()

        db.close()

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        return jsonify({
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "crm": usuario.crm
        })

    except Exception as e:
        print("ERRO GET USUARIO:", e)
        return jsonify({"erro": str(e)}), 500


# =========================
# EDITAR PERFIL
# =========================

@app.route("/usuario/<int:id>", methods=["PUT"])
def atualizar_usuario(id):

    try:

        data = request.get_json() or {}

        nome = data.get("nome")
        email = data.get("email")
        crm = data.get("crm")
        senha = data.get("senha")

        db = SessionLocal()

        if senha:

            senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

            query = text("""
            UPDATE usuarios
            SET nome = :nome,
                email = :email,
                crm = :crm,
                senha = :senha
            WHERE id = :id
            """)

            db.execute(query,{
                "nome": nome,
                "email": email,
                "crm": crm,
                "senha": senha_hash,
                "id": id
            })

        else:

            query = text("""
            UPDATE usuarios
            SET nome = :nome,
                email = :email,
                crm = :crm
            WHERE id = :id
            """)

            db.execute(query,{
                "nome": nome,
                "email": email,
                "crm": crm,
                "id": id
            })

        db.commit()
        db.close()

        return jsonify({"status": "Perfil atualizado"})

    except Exception as e:
        print("ERRO UPDATE USUARIO:", e)
        return jsonify({"erro": str(e)}), 500


# =========================
# RAG / LLM
# =========================

@app.route("/respostas-llm", methods=["POST","OPTIONS"])
def respostas_llm():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:

        data = request.get_json() or {}

        question = data.get("question","").strip()
        context = data.get("context","").strip()

        if not question:
            return jsonify({"erro": "Pergunta vazia"}), 400

        resultado = gerarRespostasLLM(
            question=question,
            context=context
        )

        if isinstance(resultado, tuple):
            return jsonify(resultado[0]), resultado[1]

        return jsonify(resultado)

    except Exception as e:
        print("ERRO LLM:", e)
        return jsonify({"erro": str(e)}), 500


# =========================
# DOENCA POR NOME
# =========================

@app.route("/doenca/<nome>", methods=["GET"])
def get_doenca(nome):

    try:

        if not nome:
            return jsonify({"erro": "Nome da doenca nao fornecido"}), 400

        from app.rag import criar_chain_rag

        rag = criar_chain_rag()
        if not rag:
            return jsonify({
                "descricao": "Sistema RAG indisponivel.",
                "sintomas": [],
                "tratamentos": [],
                "aviso": "Consulte um medico."
            })

        pergunta = (
            f"Forneca informacoes detalhadas sobre a doenca \'{nome}\'. "
            "Responda APENAS com um objeto JSON valido (sem texto extra, sem markdown, sem blocos de codigo) "
            "com os campos: descricao (string), sintomas (array de strings), "
            "tratamentos (array de strings), aviso (string)."
        )

        resultado = rag.invoke({"input": pergunta})

        texto = ""
        if isinstance(resultado, dict):
            texto = resultado.get("answer") or resultado.get("result", "")
        else:
            texto = str(resultado)

        # Tenta extrair JSON da resposta
        import re as _re2, json as _json2
        m = _re2.search(r"\{[\s\S]*\}", texto or "")
        if m:
            try:
                dados = _json2.loads(m.group())
                return jsonify(dados)
            except _json2.JSONDecodeError:
                pass

        # Fallback: retorna texto como descricao
        return jsonify({
            "descricao": texto or f"Informacoes sobre {nome} nao disponiveis.",
            "sintomas": [],
            "tratamentos": [],
            "aviso": "Consulte um medico para diagnostico correto."
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    print("\nServidor DrAignostico iniciado")
    print("API rodando em: http://localhost:8000\n")

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )

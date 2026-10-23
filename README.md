# 🩺 DrAignostico — Sistema de Apoio ao Diagnóstico Clínico com IA e RAG

O **DrAignostico** é uma plataforma médica inteligente desenvolvida para apoiar profissionais de saúde na tomada de decisão clínica. O sistema utiliza **Inteligência Artificial Generativa** combinada com **RAG (Retrieval-Augmented Generation)** sobre documentos médicos e literatura científica para sugerir diagnósticos diferenciais, detalhar sintomas, tratamentos e protocolos de alerta.

---

## 🏗️ Arquitetura do Sistema

- **Frontend:** React 19, TypeScript, Vite, React Router DOM, Lucide React.
- **Backend:** Python 3.10+, Flask, Flask-RESTX, Flask-CORS, Flask-Bcrypt, SQLAlchemy, PyMySQL.
- **Inteligência Artificial & RAG:**
  - **LLM:** Groq API (`openai/gpt-oss-120b`).
  - **Orquestração RAG:** LangChain, LangChain-Groq, LangChain-Community.
  - **Embeddings:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2`.
  - **Base Vetorial:** FAISS (`faiss-cpu`) indexando os PDFs de especialidades médicas.
- **Banco de Dados:** MySQL / MariaDB (armazena usuários, CRM, histórico de diagnósticos, pesquisas e logs).

---

## 📋 Pré-requisitos (O que instalar no seu computador)

Antes de rodar o projeto, certifique-se de ter os seguintes softwares instalados na sua máquina:

1. **Python (versão 3.10 ou 3.11 recomendada):**
   - Download: [python.org](https://www.python.org/downloads/)
   - ⚠️ **Importante no Windows:** Durante a instalação, marque a opção **"Add Python to PATH"**.
2. **Node.js (versão 18+ ou 20+ LTS) e npm:**
   - Download: [nodejs.org](https://nodejs.org/)
3. **Servidor MySQL ou MariaDB:**
   - Pode ser instalado via **XAMPP** (mais simples, basta ativar o MySQL no painel), **MySQL Workbench / Installer** ou via **Docker**.
4. **Conta e Chave de API na Groq (gratuita):**
   - Crie sua conta em [console.groq.com](https://console.groq.com/) e gere uma chave em [API Keys](https://console.groq.com/keys).
5. **Git:**
   - Download: [git-scm.com](https://git-scm.com/)

---

## 🚀 Passo a Passo de Instalação e Execução

### 1. Clonar o Repositório

Abra o terminal (PowerShell, CMD ou Bash) e clone o projeto:

```bash
git clone https://github.com/LeoTeiSil/febrace.git
cd febrace
```

---

### 2. Configurar o Banco de Dados MySQL

1. Inicie o serviço do seu MySQL (ex: pelo painel do **XAMPP** clicando em **Start** no MySQL).
2. Importe o script SQL do projeto para criar o banco de dados `sistema_diagnostico` e suas tabelas:
   - **Opção A (via phpMyAdmin / MySQL Workbench):** Abra a ferramenta, crie uma consulta SQL, copie o conteúdo de [`backend/sistema_diagnostico.sql`](backend/sistema_diagnostico.sql) e execute.
   - **Opção B (via terminal MySQL):**
     ```bash
     mysql -u root -p < backend/sistema_diagnostico.sql
     ```

As tabelas criadas são:
- `usuarios` (médicos cadastrados, CRM, hash de senha)
- `historico_diagnostico` (diagnósticos sugeridos e sintomas)
- `pesquisas` (histórico de buscas)
- `perguntas_rag` e `dados` (histórico de consultas e respostas da IA)

---

### 3. Configurar as Variáveis de Ambiente (`.env`)

Na raiz do projeto (`febrace/`), crie um arquivo chamado `.env` (ou copie de `.env.example`):

```bash
cp .env.example .env
```

Abra o `.env` e configure com suas credenciais:

```env
# Chave da API da Groq (obrigatória)
GROQ_API_KEY=gsk_sua_chave_groq_aqui

# Conexão com o Banco de Dados MySQL
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sistema_diagnostico
```

---

### 4. Configurar e Executar o Backend (Python / Flask)

1. Entre na pasta do backend:
   ```bash
   cd backend
   ```

2. Crie e ative um ambiente virtual:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Atualize o `pip` e instale as dependências:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Gerar a Base de Vetores RAG (Vetorização dos PDFs Médicos):**
   > Esta etapa lê todos os PDFs da pasta `backend/dados/` e cria o índice de busca vetorial FAISS em `backend/vetores_doencas/`.

   Execute:
   ```bash
   python vetorizador.py
   ```
   *Aguarde a mensagem: `✅ VETORIZAÇÃO CONCLUÍDA COM SUCESSO!`*

5. **Iniciar o Servidor Backend:**
   ```bash
   python run.py
   ```
   O backend iniciará em: **`http://localhost:8000`**

---

### 5. Configurar e Executar o Frontend (React / Vite)

Abra um **segundo terminal** (mantenha o backend rodando no primeiro):

1. Vá até a pasta do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências do Node.js:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

4. Abra no seu navegador o endereço indicado (geralmente **`http://localhost:5173`**).

---

## 📁 Estrutura do Projeto

```text
febrace/
├── .env.example                # Exemplo das variáveis de ambiente
├── .gitignore                  # Arquivos ignorados pelo Git (venv, .env, caches)
├── README.md                   # Documentação completa do projeto
├── backend/
│   ├── app/
│   │   ├── __init__.py         # Inicialização do Flask e rotas centrais
│   │   ├── config.py           # Configurações de banco e diretórios
│   │   ├── database.py         # Conexão SQLAlchemy
│   │   ├── models.py           # Modelos de dados ORM
│   │   ├── rag.py              # Pipeline RAG (LangChain + FAISS + Groq)
│   │   └── api/                # Endpoints e serviços modulares
│   ├── dados/                  # PDFs com literatura médica (divididos por categorias)
│   ├── vetores_doencas/        # Índices FAISS gerados pelo vetorizador
│   ├── requirements.txt        # Dependências Python do projeto
│   ├── run.py                  # Ponto de entrada do servidor backend (porta 8000)
│   ├── sistema_diagnostico.sql # Script de criação do banco e tabelas MySQL
│   └── vetorizador.py          # Script de processamento e indexação de PDFs
└── frontend/
    ├── src/
    │   ├── components/         # Navbar, Sidebar, Layout do dashboard
    │   ├── pages/              # Páginas: Analise, Diagnosticos, Informacoes, Login, etc.
    │   ├── styles/             # Arquivos CSS de estilização
    │   ├── App.tsx             # Roteador principal da aplicação
    │   └── main.tsx            # Ponto de entrada React
    ├── package.json            # Dependências e scripts do frontend
    └── vite.config.ts          # Configuração do Vite
```

---

## 🔌 Principais Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status da API e listagem de rotas disponíveis |
| `POST` | `/cadastro` | Cadastra um novo médico (`nome`, `email`, `senha`, `crm`) |
| `POST` | `/login` | Autenticação com verificação de hash Bcrypt |
| `POST` | `/recuperar-senha` | Redefinição de senha por CRM e e-mail |
| `POST` | `/respostas-llm` | Envia sintomas do paciente e retorna diagnósticos sugeridos via RAG |
| `GET` | `/doenca/<nome>` | Retorna JSON estruturado com descrição, sintomas, tratamentos e avisos da doença |
| `GET` | `/usuario/<id>` | Consulta os dados do perfil do médico |
| `PUT` | `/usuario/<id>` | Atualiza dados e/ou senha do perfil |

---

## 🛠️ Solução de Problemas Comuns

### 1. Erro `Table 'sistema_diagnostico.dados' doesn't exist`
Execute o script [`backend/sistema_diagnostico.sql`](backend/sistema_diagnostico.sql) no seu MySQL para criar as tabelas necessárias.

### 2. Erro Groq `The model does not exist or you do not have access to it`
O modelo configurado no pipeline RAG é o `openai/gpt-oss-120b`, disponível gratuitamente na API da Groq. Certifique-se de que sua `GROQ_API_KEY` no `.env` está correta e ativa.

### 3. Erro `Índice FAISS não encontrado` ao iniciar o backend
Você precisa rodar a indexação dos PDFs antes de subir a API:
```powershell
cd backend
python vetorizador.py
```

### 4. Erro de Execução de Scripts no PowerShell (`Activate.ps1`)
Se o PowerShell bloquear a ativação do ambiente virtual, execute uma vez no terminal como administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 👥 Equipe & Projeto
Projeto desenvolvido no âmbito da **FEBRACE** para auxílio ao diagnóstico clínico médico.

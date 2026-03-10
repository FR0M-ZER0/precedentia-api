# PrecedentIA - API

API do sistema **PrecedentIA**, desenvolvida em FastAPI, responsável por fornecer os dados e regras de negócio para busca e visualização de precedentes jurídicos.

## 🚀 Tecnologias Utilizadas

O projeto utiliza as seguintes tecnologias e bibliotecas:

- **FastAPI** - Framework web moderno e de alta performance para construção de APIs
- **Pydantic** - Validação de dados e serialização via modelos tipados
- **SQLAlchemy** - ORM para comunicação com o banco de dados
- **PyJWT** - Geração e validação de tokens JWT para autenticação
- **Python-dotenv** - Gerenciamento de variáveis de ambiente via arquivo `.env`
- **Pytest** - Framework de testes para testes unitários e de integração


## ⚙️ Rodando o Projeto

### 1️⃣ Verifique o ambiente Python

Execute o comando abaixo para garantir que está utilizando a versão correta do Python (3.11+):

```bash
python --version
```

### 2️⃣ Crie e ative o ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 3️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com os valores adequados:

```bash
cp .env.example .env
```

### 5️⃣ Execute a aplicação

```bash
fastapi dev app/main.py
```

A API estará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

## 🧪 Rodando os testes

Para executar a suite de testes do projeto:

```bash
pytest
```

Para rodar com cobertura de código:

```bash
pytest --cov=app
```

## 📦 Build para produção

Para rodar em ambiente de produção:

```bash
fastapi run app/main.py --port 8000
```

## Saiba mais

Para verificar as padronizações usadas neste projeto, bem como demais documentações, visite o nosso [repositório principal](https://github.com/FR0M-ZER0/PrecedentIA)
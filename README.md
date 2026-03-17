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

## 🏗️ Arquitetura

O projeto segue a seguinte estrutura:

    app/
    ├── api/
    │   ├── endpoints
    │   └── router.py
    ├── core/
    │   ├── config.py
    │   └── database.py
    ├── models/
    │   └── user_model.py
    ├── repositories/
    │   └── user_repository.py
    ├── schemas/
    │   └── user_schema.py
    ├── security/
    │   └── validation.py
    ├── services/
    │   └── user_service.py
    ├── utils/
    │   ├── formatter.py
    │   ├── pagination.py
    │   └── hateoas.py
    └── main.py

### Camadas da Arquitetura

**Api** - Contém as rotas e endpoints responsáveis por receber as requisições HTTP e encaminhá-las para as camadas apropriadas da aplicação.

**Core** - Contém configurações globais do projeto, como configuração do banco de dados, variáveis de ambiente, inicialização de serviços e outras definições centrais.

**Models** - Contém os modelos que representam as entidades do banco de dados. Normalmente são utilizados pelo ORM para mapear tabelas e relacionamentos.

**Repositories** - Responsáveis pela comunicação direta com o banco de dados. Implementam as operações de acesso a dados (CRUD), isolando a lógica de persistência do restante da aplicação.

**Schemas** - Definem os modelos de dados utilizados para validação, serialização e desserialização das requisições e respostas da API. São usados para validar entrada de dados e estruturar respostas.

**Security** - Contém funcionalidades relacionadas à segurança da aplicação, como validação de tokens, autenticação, autorização e outras regras de proteção.

**Services** - Contém a lógica de negócio da aplicação. Essa camada coordena regras de negócio e utiliza os repositórios para acessar os dados.

**Utils** - Reúne funções utilitárias e helpers reutilizáveis em diferentes partes do sistema, como formatação de dados, paginação e implementação de padrões como HATEOAS.

## ⚙️ Rodando o Projeto

### 1️⃣ Verifique o ambiente Python

Execute o comando abaixo para garantir que está utilizando a versão correta do Python (3.12+):

```bash
python --version
```

### 2️⃣ Instale as dependências do Node

O projeto faz uso do Husky para gerenciar os hooks do git, bem como do commitlint. Instale esses pacotes usando:

```bash
npm i
```

Depois rode o seguinte comando para ativar o Husky:

```bash
npm run prepare
```

> **Atenção:** É necessário ativar o ambiente virtual do python para poder fazer os commits!

> **Atenção:** É necessário rodar o npm i antes de criar a venv!

### 3️⃣ Crie e ative o ambiente virtual

```bash
python -m venv .venv       # ou python3 no Linux
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 4️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 5️⃣ Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com os valores adequados:

```bash
cp .env.example .env
```

### 6️⃣ Execute a aplicação

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
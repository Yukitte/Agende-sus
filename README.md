# AgendeSUS DF - Sistema de Agendamento de Cirurgias

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)

O **AgendeSUS DF** é um sistema web desenvolvido em Python com o framework Flask, projetado para otimizar e digitalizar o processo de agendamento, acompanhamento e gestão de procedimentos cirúrgicos na rede pública de saúde do Distrito Federal.

## ✨ Funcionalidades Principais

- **Autenticação e Perfis de Usuário**: Sistema de login seguro com diferentes níveis de acesso (Paciente, Médico, Administrador).
- **Agendamento Simplificado**: Pacientes podem solicitar o agendamento de cirurgias de forma intuitiva.
- **Painel do Paciente**: Visualização do histórico e status dos agendamentos.
- **Sistema de Notificações**: Envio de e-mails e alertas na plataforma para confirmações, cancelamentos e lembretes de cirurgias.
- **Gestão de Vagas**: O sistema gerencia a capacidade cirúrgica dos hospitais, evitando sobrecarga.
- **Lista de Espera Automatizada**: Quando uma vaga é cancelada, o sistema pode realocar automaticamente o próximo paciente da fila de espera.
- **Controle de Acesso**: Arquitetura robusta que garante que cada usuário acesse apenas as informações pertinentes ao seu perfil.

## 🚀 Tecnologias Utilizadas

- **Backend**: Python 3, Flask
- **Banco de Dados**: Flask-SQLAlchemy (compatível com SQLite, PostgreSQL, MySQL)
- **Templates**: Jinja2, HTML5
- **Estilização**: Bootstrap 5
- **Comunicação**: Flask-Mail (para envio de e-mails)

## ⚙️ Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

- [Python 3.8+](https://www.python.org/downloads/)
- `pip` (gerenciador de pacotes do Python)
- `git` (para clonar o repositório)

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd AgendeSus/backend
    ```

2.  **Crie e ative um ambiente virtual:**
    É uma boa prática isolar as dependências do projeto.

    ```bash
    # Criar o ambiente
    python -m venv venv

    # Ativar no Windows
    .\venv\Scripts\activate

    # Ativar no Linux/macOS
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    O arquivo `requirements.txt` contém todas as bibliotecas Python necessárias.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Crie o banco de dados:**
    O projeto utiliza o Flask-Migrate (ou comandos CLI) para gerenciar o schema do banco. O comando abaixo criará o arquivo `agendesus.db` (SQLite) e as tabelas.
    ```bash
    flask create-tables
    ```
    *Nota: Este comando foi definido em `app_init.py`.*

## ▶️ Executando a Aplicação

Com o ambiente virtual ativado e as dependências instaladas, inicie o servidor de desenvolvimento:

```bash
python app.py
```

A aplicação estará disponível em **http://127.0.0.1:5000**.

### Contas de Teste

Se os dados iniciais forem populados, você pode usar as seguintes credenciais:
- **Admin**: `admin@saude.df.gov.br` / `admin123`
- **Médico**: `medico@saude.df.gov.br` / `medico123`
- **Paciente**: `paciente@teste.com` / `paciente123`

## 📂 Estrutura do Projeto

O projeto segue uma estrutura organizada para facilitar a manutenção e escalabilidade:

```
backend/
├── templates/         # Arquivos HTML (templates Jinja2)
├── static/            # Arquivos estáticos (CSS, JS, imagens)
├── app.py             # Ponto de entrada principal da aplicação
├── app_init.py        # Fábrica da aplicação (Application Factory)
├── app_config.py      # Configurações (dev, prod, test)
├── models_*.py        # Modelos de dados (schema do banco com SQLAlchemy)
├── controllers_*.py   # Lógica de negócio da aplicação
├── routes_*.py        # Definição das rotas e endpoints (Blueprints)
├── utils_decorators.py# Decoradores para controle de acesso e autenticação
└── requirements.txt   # Lista de dependências do projeto
```

## 🔧 Comandos CLI

O Flask CLI foi estendido com comandos úteis:

- `flask create-tables`: Cria todas as tabelas no banco de dados.
- `flask drop-tables`: **CUIDADO!** Remove todas as tabelas e dados.
- `flask seed-data`: (A ser implementado) Popula o banco com dados iniciais para teste.

---


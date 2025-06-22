"""
AgendeSUS DF - Configurações da Aplicação
Arquivo de configuração centralizada do sistema
"""

import os
from datetime import timedelta

class Config:
    """Configuração base da aplicação"""
    
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'agendesus-df-2025-secretkey'
    
    # Configurações do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///agendesus.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    
    # Configurações de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'agendesus@saude.df.gov.br'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'senha123'
    MAIL_DEFAULT_SENDER = 'agendesus@saude.df.gov.br'
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Configurações de paginação
    ITEMS_PER_PAGE = 10
    MAX_SEARCH_RESULTS = 50
    
    # Configurações do sistema
    SISTEMA_NOME = 'AgendeSUS DF'
    SISTEMA_VERSAO = '1.0.0'
    ORGAO_RESPONSAVEL = 'Secretaria de Saúde do Distrito Federal'
    
    # Configurações de segurança
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora
    
    # Configurações de cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Configurações de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = 'agendesus.log'
    
    # Configurações específicas do negócio
    DIAS_ANTECEDENCIA_MINIMA = 1  # Dias mínimos para agendar
    DIAS_ANTECEDENCIA_MAXIMA = 180  # Dias máximos para agendar
    HORARIO_FUNCIONAMENTO_INICIO = 7  # 7h
    HORARIO_FUNCIONAMENTO_FIM = 18  # 18h
    INTERVALO_AGENDAMENTO = 30  # 30 minutos
    
    # Configurações de notificação
    HORAS_ANTECEDENCIA_LEMBRETE = 24  # Lembrete 24h antes
    DIAS_ANTECEDENCIA_CONFIRMACAO = 3  # Confirmar 3 dias antes
    
    # Especialidades médicas disponíveis
    ESPECIALIDADES = [
        'Cardiologia',
        'Ortopedia', 
        'Neurologia',
        'Oftalmologia',
        'Ginecologia',
        'Urologia',
        'Dermatologia',
        'Pediatria',
        'Psiquiatria',
        'Oncologia',
        'Endocrinologia',
        'Gastroenterologia'
    ]
    
    # Tipos de cirurgia por especialidade
    TIPOS_CIRURGIA = {
        'Cardiologia': [
            'Angioplastia',
            'Bypass Coronário',
            'Troca de Válvula',
            'Marcapasso',
            'Desfibrilador'
        ],
        'Ortopedia': [
            'Artroscopia',
            'Prótese de Quadril',
            'Prótese de Joelho',
            'Correção de Fratura',
            'Cirurgia de Coluna'
        ],
        'Neurologia': [
            'Craniotomia',
            'Clipagem de Aneurisma',
            'Tumor Cerebral',
            'Cirurgia de Epilepsia',
            'Derivação Ventricular'
        ],
        'Oftalmologia': [
            'Catarata',
            'Glaucoma',
            'Retina',
            'Córnea',
            'Pterígio'
        ],
        'Ginecologia': [
            'Histerectomia',
            'Cesariana',
            'Laparoscopia',
            'Miomectomia',
            'Ooforectomia'
        ],
        'Urologia': [
            'Prostatectomia',
            'Nefrectomia',
            'Cistectomia',
            'Litotripsia',
            'Vasectomia'
        ]
    }
    
    # Níveis de prioridade
    NIVEIS_PRIORIDADE = {
        1: 'Baixa',
        2: 'Média', 
        3: 'Alta',
        4: 'Urgente',
        5: 'Emergência'
    }
    
    # Status de agendamento
    STATUS_AGENDAMENTO = [
        'agendado',
        'confirmado',
        'em_andamento',
        'concluido',
        'cancelado',
        'reagendado'
    ]
    
    # Tipos de usuário
    TIPOS_USUARIO = [
        'paciente',
        'medico',
        'enfermeiro',
        'admin',
        'gestor'
    ]

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False
    
    # Database mais verboso em desenvolvimento
    SQLALCHEMY_ECHO = True
    
    # Email em desenvolvimento (não envia realmente)
    MAIL_SUPPRESS_SEND = True
    
    # Cache desabilitado em desenvolvimento
    CACHE_TYPE = 'null'

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    DEBUG = True
    
    # Banco em memória para testes
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Desabilitar CSRF em testes
    WTF_CSRF_ENABLED = False
    
    # Email não é enviado em testes
    MAIL_SUPPRESS_SEND = True
    
    # Cache desabilitado em testes
    CACHE_TYPE = 'null'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    
    # Configurações de segurança para produção
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database otimizado para produção
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    
    # Logging mais rigoroso em produção
    LOG_LEVEL = 'WARNING'
    
    # Email real em produção
    MAIL_SUPPRESS_SEND = False

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retorna a configuração baseada na variável de ambiente"""
    return config[os.environ.get('FLASK_CONFIG') or 'default']
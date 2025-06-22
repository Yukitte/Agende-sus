"""
AgendeSUS DF - Modelo de Usuários
Definição da estrutura de dados para usuários do sistema
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    """Modelo principal de usuários do sistema"""
    
    __tablename__ = 'usuarios'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(15))
    senha_hash = db.Column(db.String(255), nullable=False)
    
    # Tipo e status
    tipo_usuario = db.Column(db.String(20), nullable=False, index=True)  # 'paciente', 'medico', 'admin', etc.
    ativo = db.Column(db.Boolean, default=True, nullable=False, index=True)
    email_verificado = db.Column(db.Boolean, default=False)
    
    # Dados adicionais
    foto_perfil = db.Column(db.String(200))  # URL da foto
    endereco_completo = db.Column(db.Text)
    data_nascimento = db.Column(db.Date)
    genero = db.Column(db.String(10))  # 'M', 'F', 'Outro'
    
    # Timestamps
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultimo_acesso = db.Column(db.DateTime)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configurações de conta
    receber_emails = db.Column(db.Boolean, default=True)
    receber_sms = db.Column(db.Boolean, default=True)
    tema_preferido = db.Column(db.String(20), default='claro')  # 'claro', 'escuro'
    
    # Campos de auditoria
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    ip_cadastro = db.Column(db.String(45))
    user_agent_cadastro = db.Column(db.String(500))
    
    # Relacionamentos
    paciente = db.relationship('Paciente', backref='usuario', uselist=False, lazy='select')
    profissional = db.relationship('ProfissionalSaude', backref='usuario', uselist=False, lazy='select')
    notificacoes = db.relationship('Notificacao', backref='usuario', lazy='dynamic')
    mensagens_enviadas = db.relationship('Chat', backref='remetente', lazy='dynamic')
    logs_acesso = db.relationship('LogAcesso', backref='usuario', lazy='dynamic')
    
    # Relacionamento auto-referencial para criado_por
    criador = db.relationship('Usuario', remote_side=[id], backref='usuarios_criados')
    
    def __init__(self, **kwargs):
        super(Usuario, self).__init__(**kwargs)
        if self.data_cadastro is None:
            self.data_cadastro = datetime.utcnow()
    
    def __repr__(self):
        return f'<Usuario {self.nome} ({self.email})>'
    
    # Métodos de senha
    def set_password(self, senha):
        """Define a senha do usuário"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_password(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    # Métodos de validação
    def is_active(self):
        """Verifica se o usuário está ativo"""
        return self.ativo
    
    def is_authenticated(self):
        """Verifica se o usuário está autenticado"""
        return True
    
    def is_anonymous(self):
        """Verifica se é usuário anônimo"""
        return False
    
    def get_id(self):
        """Retorna o ID do usuário como string"""
        return str(self.id)
    
    # Métodos de permissão
    def is_admin(self):
        """Verifica se é administrador"""
        return self.tipo_usuario == 'admin'
    
    def is_medico(self):
        """Verifica se é médico"""
        return self.tipo_usuario in ['medico', 'enfermeiro']
    
    def is_paciente(self):
        """Verifica se é paciente"""
        return self.tipo_usuario == 'paciente'
    
    def is_gestor(self):
        """Verifica se é gestor"""
        return self.tipo_usuario in ['admin', 'gestor']
    
    def can_access_admin(self):
        """Verifica se pode acessar área administrativa"""
        return self.tipo_usuario in ['admin', 'gestor']
    
    def can_manage_users(self):
        """Verifica se pode gerenciar usuários"""
        return self.tipo_usuario == 'admin'
    
    def can_view_reports(self):
        """Verifica se pode visualizar relatórios"""
        return self.tipo_usuario in ['admin', 'gestor', 'medico']
    
    # Métodos de dados
    def get_nome_completo(self):
        """Retorna o nome completo do usuário"""
        return self.nome
    
    def get_nome_display(self):
        """Retorna nome para exibição (primeiro nome + último sobrenome)"""
        partes = self.nome.split()
        if len(partes) > 1:
            return f"{partes[0]} {partes[-1]}"
        return partes[0] if partes else ""
    
    def get_iniciais(self):
        """Retorna as iniciais do nome"""
        partes = self.nome.split()
        iniciais = ''.join([parte[0].upper() for parte in partes if parte])
        return iniciais[:2]  # Máximo 2 letras
    
    def get_idade(self):
        """Calcula e retorna a idade do usuário"""
        if not self.data_nascimento:
            return None
        
        hoje = datetime.now().date()
        idade = hoje.year - self.data_nascimento.year
        
        if hoje < self.data_nascimento.replace(year=hoje.year):
            idade -= 1
            
        return idade
    
    def get_tempo_cadastro(self):
        """Retorna há quanto tempo o usuário está cadastrado"""
        if not self.data_cadastro:
            return None
            
        delta = datetime.utcnow() - self.data_cadastro
        
        if delta.days > 365:
            anos = delta.days // 365
            return f"{anos} ano{'s' if anos > 1 else ''}"
        elif delta.days > 30:
            meses = delta.days // 30
            return f"{meses} mês{'es' if meses > 1 else ''}"
        elif delta.days > 0:
            return f"{delta.days} dia{'s' if delta.days > 1 else ''}"
        else:
            horas = delta.seconds // 3600
            return f"{horas} hora{'s' if horas > 1 else ''}"
    
    # Métodos de atividade
    def registrar_acesso(self, ip_address=None, user_agent=None):
        """Registra o último acesso do usuário"""
        self.ultimo_acesso = datetime.utcnow()
        
        # Criar log de acesso
        if ip_address or user_agent:
            log = LogAcesso(
                usuario_id=self.id,
                ip_address=ip_address,
                user_agent=user_agent,
                data_acesso=datetime.utcnow()
            )
            db.session.add(log)
    
    def get_notificacoes_nao_lidas(self):
        """Retorna o número de notificações não lidas"""
        return self.notificacoes.filter_by(lida=False).count()
    
    def marcar_notificacoes_como_lidas(self):
        """Marca todas as notificações como lidas"""
        self.notificacoes.filter_by(lida=False).update({'lida': True})
        db.session.commit()
    
    # Métodos de serialização
    def to_dict(self, include_sensitive=False):
        """Converte o usuário para dicionário"""
        data = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email if include_sensitive else None,
            'tipo_usuario': self.tipo_usuario,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'iniciais': self.get_iniciais(),
            'nome_display': self.get_nome_display()
        }
        
        if include_sensitive:
            data.update({
                'cpf': self.cpf,
                'telefone': self.telefone,
                'endereco_completo': self.endereco_completo,
                'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
                'genero': self.genero,
                'email_verificado': self.email_verificado,
                'receber_emails': self.receber_emails,
                'receber_sms': self.receber_sms
            })
        
        return data
    
    @staticmethod
    def buscar_por_email(email):
        """Busca usuário por email"""
        return Usuario.query.filter_by(email=email.lower(), ativo=True).first()
    
    @staticmethod
    def buscar_por_cpf(cpf):
        """Busca usuário por CPF"""
        # Remove formatação do CPF
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        return Usuario.query.filter_by(cpf=cpf_limpo, ativo=True).first()
    
    @staticmethod
    def validar_cpf(cpf):
        """Valida CPF (algoritmo básico)"""
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Validação dos dígitos verificadores
        def calcular_digito(cpf, peso_inicial):
            soma = sum(int(cpf[i]) * (peso_inicial - i) for i in range(len(cpf)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        if int(cpf[9]) != calcular_digito(cpf[:9], 10):
            return False
        
        if int(cpf[10]) != calcular_digito(cpf[:10], 11):
            return False
        
        return True
    
    @staticmethod
    def email_existe(email, excluir_id=None):
        """Verifica se email já existe"""
        query = Usuario.query.filter_by(email=email.lower())
        if excluir_id:
            query = query.filter(Usuario.id != excluir_id)
        return query.first() is not None
    
    @staticmethod
    def cpf_existe(cpf, excluir_id=None):
        """Verifica se CPF já existe"""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        query = Usuario.query.filter_by(cpf=cpf_limpo)
        if excluir_id:
            query = query.filter(Usuario.id != excluir_id)
        return query.first() is not None

class LogAcesso(db.Model):
    """Modelo para registrar acessos dos usuários"""
    
    __tablename__ = 'logs_acesso'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    data_acesso = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    acao = db.Column(db.String(100))  # 'login', 'logout', 'acesso_pagina'
    detalhes = db.Column(db.Text)  # Detalhes adicionais em JSON
    
    def __repr__(self):
        return f'<LogAcesso {self.usuario_id} - {self.data_acesso}>'
    
    @staticmethod
    def registrar(usuario_id, acao, ip_address=None, user_agent=None, detalhes=None):
        """Registra um log de acesso"""
        log = LogAcesso(
            usuario_id=usuario_id,
            acao=acao,
            ip_address=ip_address,
            user_agent=user_agent,
            detalhes=detalhes
        )
        db.session.add(log)
        return log

class PreferenciasUsuario(db.Model):
    """Modelo para preferências personalizadas do usuário"""
    
    __tablename__ = 'preferencias_usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    chave = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índice único para usuario_id + chave
    __table_args__ = (db.UniqueConstraint('usuario_id', 'chave'),)
    
    # Relacionamento
    usuario = db.relationship('Usuario', backref='preferencias')
    
    def __repr__(self):
        return f'<PreferenciasUsuario {self.usuario_id}:{self.chave}>'
    
    @staticmethod
    def definir(usuario_id, chave, valor):
        """Define uma preferência do usuário"""
        preferencia = PreferenciasUsuario.query.filter_by(
            usuario_id=usuario_id, chave=chave
        ).first()
        
        if preferencia:
            preferencia.valor = valor
            preferencia.data_atualizacao = datetime.utcnow()
        else:
            preferencia = PreferenciasUsuario(
                usuario_id=usuario_id,
                chave=chave,
                valor=valor
            )
            db.session.add(preferencia)
        
        return preferencia
    
    @staticmethod
    def obter(usuario_id, chave, padrao=None):
        """Obtém uma preferência do usuário"""
        preferencia = PreferenciasUsuario.query.filter_by(
            usuario_id=usuario_id, chave=chave
        ).first()
        
        return preferencia.valor if preferencia else padrao
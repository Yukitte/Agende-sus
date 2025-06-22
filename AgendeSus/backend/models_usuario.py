"""
AgendeSUS DF - Modelos de Usuário
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import db

class Usuario(db.Model):
    """Modelo base para todos os usuários do sistema"""
    
    __tablename__ = 'usuarios'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(15))
    senha_hash = db.Column(db.String(255), nullable=False)
    
    # Tipo de usuário
    tipo_usuario = db.Column(db.String(20), nullable=False, index=True)  # 'paciente', 'medico', 'admin'
    
    # Timestamps e status
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ultimo_login = db.Column(db.DateTime)
    ativo = db.Column(db.Boolean, default=True, index=True)
    
    # Relacionamentos
    paciente = db.relationship('Paciente', backref='usuario', uselist=False, cascade='all, delete-orphan')
    profissional = db.relationship('ProfissionalSaude', backref='usuario', uselist=False, cascade='all, delete-orphan')
    notificacoes = db.relationship('Notificacao', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    mensagens_enviadas = db.relationship('Chat', backref='remetente', lazy='dynamic')
    
    def __init__(self, **kwargs):
        """Inicializa um novo usuário"""
        super(Usuario, self).__init__(**kwargs)
        
    def __repr__(self):
        return f'<Usuario {self.nome} ({self.email})>'
    
    def set_password(self, password):
        """Define a senha do usuário (com hash)"""
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, password)
    
    def update_last_login(self):
        """Atualiza o timestamp do último login"""
        self.ultimo_login = datetime.utcnow()
        db.session.commit()
    
    def is_active(self):
        """Verifica se o usuário está ativo"""
        return self.ativo
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.tipo_usuario == 'admin'
    
    def is_paciente(self):
        """Verifica se o usuário é paciente"""
        return self.tipo_usuario == 'paciente'
    
    def is_medico(self):
        """Verifica se o usuário é médico"""
        return self.tipo_usuario == 'medico'
    
    def get_notificacoes_nao_lidas(self):
        """Retorna o número de notificações não lidas"""
        return self.notificacoes.filter_by(lida=False).count()
    
    def to_dict(self):
        """Converte o usuário para dicionário (para APIs)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'tipo_usuario': self.tipo_usuario,
            'data_cadastro': self.data_cadastro,
            'ultimo_login': self.ultimo_login,
            'ativo': self.ativo
        }
    
    @staticmethod
    def get_by_email(email):
        """Busca usuário pelo email"""
        return Usuario.query.filter_by(email=email).first()
    
    @staticmethod
    def get_by_cpf(cpf):
        """Busca usuário pelo CPF"""
        return Usuario.query.filter_by(cpf=cpf).first()
    
    @staticmethod
    def create_user(nome, email, cpf, telefone, senha, tipo_usuario):
        """Cria um novo usuário"""
        try:
            usuario = Usuario(
                nome=nome,
                email=email,
                cpf=cpf,
                telefone=telefone,
                tipo_usuario=tipo_usuario
            )
            usuario.set_password(senha)
            
            db.session.add(usuario)
            db.session.commit()
            
            return {'success': True, 'usuario': usuario}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

class Paciente(db.Model):
    """Modelo específico para pacientes"""
    
    __tablename__ = 'pacientes'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    
    # Dados específicos do paciente
    cartao_sus = db.Column(db.String(15), unique=True, nullable=False, index=True)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.Text)
    cidade = db.Column(db.String(100))
    cep = db.Column(db.String(8))
    
    # Informações médicas
    historico_medico = db.Column(db.Text)
    alergias = db.Column(db.Text)
    medicamentos_uso = db.Column(db.Text)
    
    # Contato de emergência
    contato_emergencia_nome = db.Column(db.String(100))
    contato_emergencia_telefone = db.Column(db.String(15))
    contato_emergencia_parentesco = db.Column(db.String(50))
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy='dynamic', cascade='all, delete-orphan')
    lista_espera = db.relationship('ListaEspera', backref='paciente', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Paciente {self.usuario.nome} - SUS: {self.cartao_sus}>'
    
    def get_idade(self):
        """Calcula a idade do paciente"""
        from datetime import date
        today = date.today()
        return today.year - self.data_nascimento.year - (
            (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
    
    def get_agendamentos_ativos(self):
        """Retorna agendamentos não cancelados"""
        return self.agendamentos.filter(
            db.and_(
                db.or_(
                    db.text("agendamentos.status = 'agendado'"),
                    db.text("agendamentos.status = 'confirmado'")
                )
            )
        ).order_by(db.text("agendamentos.data_cirurgia"))
    
    def get_historico_cirurgias(self):
        """Retorna histórico de cirurgias realizadas"""
        return self.agendamentos.filter_by(status='realizado').order_by(
            db.text("agendamentos.data_cirurgia DESC")
        )
    
    def tem_lista_espera_ativa(self, especialidade=None):
        """Verifica se está em lista de espera"""
        query = self.lista_espera.filter_by(ativa=True)
        if especialidade:
            query = query.filter_by(especialidade=especialidade)
        return query.first() is not None
    
    def to_dict(self):
        """Converte paciente para dicionário"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'cartao_sus': self.cartao_sus,
            'data_nascimento': self.data_nascimento,
            'idade': self.get_idade(),
            'endereco': self.endereco,
            'cidade': self.cidade,
            'cep': self.cep,
            'historico_medico': self.historico_medico,
            'alergias': self.alergias,
            'medicamentos_uso': self.medicamentos_uso,
            'contato_emergencia': {
                'nome': self.contato_emergencia_nome,
                'telefone': self.contato_emergencia_telefone,
                'parentesco': self.contato_emergencia_parentesco
            }
        }

class ProfissionalSaude(db.Model):
    """Modelo específico para profissionais de saúde"""
    
    __tablename__ = 'profissionais_saude'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    
    # Dados profissionais
    registro_profissional = db.Column(db.String(20), unique=True, nullable=False, index
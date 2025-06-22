# models/agendamento.py
from datetime import datetime
from app_init import db

class Hospital(db.Model):
    __tablename__ = 'hospitais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.String(15))
    especialidades = db.Column(db.Text)  # JSON string com especialidades
    capacidade_cirurgica = db.Column(db.Integer, default=10)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    profissionais = db.relationship('ProfissionalSaude', backref='hospital', lazy=True)
    agendamentos = db.relationship('Agendamento', backref='hospital', lazy=True)
    
    def __repr__(self):
        return f'<Hospital {self.nome}>'

class EquipeCirurgia(db.Model):
    __tablename__ = 'equipes_cirurgia'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativa = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    membros = db.relationship('ProfissionalSaude', secondary='equipe_membros', back_populates='equipes')
    agendamentos = db.relationship('Agendamento', backref='equipe', lazy=True)
    
    def __repr__(self):
        return f'<EquipeCirurgia {self.nome}>'

# Tabela de associação para equipes e membros
equipe_membros = db.Table('equipe_membros',
    db.Column('equipe_id', db.Integer, db.ForeignKey('equipes_cirurgia.id'), primary_key=True),
    db.Column('profissional_id', db.Integer, db.ForeignKey('profissionais_saude.id'), primary_key=True)
)

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitais.id'), nullable=False)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipes_cirurgia.id'))
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais_saude.id'))
    
    data_cirurgia = db.Column(db.DateTime, nullable=False)
    tipo_cirurgia = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    urgencia = db.Column(db.String(20), default='eletiva')  # 'eletiva' ou 'urgencia'
    status = db.Column(db.String(20), default='agendado')  # 'agendado', 'confirmado', 'cancelado', 'realizado'
    
    observacoes = db.Column(db.Text)
    data_agendamento = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    notificacoes = db.relationship('Notificacao', backref='agendamento', lazy=True)
    mensagens_chat = db.relationship('Chat', backref='agendamento', lazy=True)
    
    def __repr__(self):
        return f'<Agendamento {self.id} - {self.tipo_cirurgia}>'
    
    @property
    def pode_cancelar(self):
        """Verifica se o agendamento pode ser cancelado"""
        return self.status in ['agendado', 'confirmado'] and self.data_cirurgia > datetime.now()
    
    @property
    def status_display(self):
        """Retorna status formatado para exibição"""
        status_map = {
            'agendado': 'Agendado',
            'confirmado': 'Confirmado',
            'cancelado': 'Cancelado',
            'realizado': 'Realizado'
        }
        return status_map.get(self.status, self.status.title())

class ListaEspera(db.Model):
    __tablename__ = 'lista_espera'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    tipo_cirurgia = db.Column(db.String(100), nullable=False)
    prioridade = db.Column(db.Integer, default=1)  # 1=baixa, 2=média, 3=alta
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    ativa = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    paciente = db.relationship('Paciente', backref='lista_espera')
    
    def __repr__(self):
        return f'<ListaEspera {self.id} - {self.especialidade}>'
    
    @property
    def prioridade_display(self):
        """Retorna prioridade formatada para exibição"""
        prioridade_map = {
            1: 'Baixa',
            2: 'Média', 
            3: 'Alta'
        }
        return prioridade_map.get(self.prioridade, 'Baixa')

class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'))
    
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), default='info')  # 'info', 'lembrete', 'cancelamento'
    lida = db.Column(db.Boolean, default=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='notificacoes')
    
    def __repr__(self):
        return f'<Notificacao {self.id} - {self.titulo}>'
    
    @property
    def tipo_display(self):
        """Retorna tipo formatado para exibição"""
        tipo_map = {
            'info': 'Informação',
            'lembrete': 'Lembrete',
            'cancelamento': 'Cancelamento',
            'urgente': 'Urgente'
        }
        return tipo_map.get(self.tipo, 'Info')

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=False)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    remetente = db.relationship('Usuario', backref='mensagens_enviadas')
    
    def __repr__(self):
        return f'<Chat {self.id} - Agendamento {self.agendamento_id}>'
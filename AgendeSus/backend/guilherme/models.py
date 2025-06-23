from app import db
from datetime import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    genero = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cartao_sus = db.Column(db.String(20), unique=True)
    tipo_usuario = db.Column(db.String(20), default='paciente')  # paciente, medico, admin
    receber_emails = db.Column(db.Boolean, default=True)
    receber_sms = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy=True)
    notificacoes = db.relationship('Notificacao', backref='usuario', lazy=True)
    mensagens_enviadas = db.relationship('Mensagem', foreign_keys='Mensagem.remetente_id', backref='remetente', lazy=True)
    mensagens_recebidas = db.relationship('Mensagem', foreign_keys='Mensagem.destinatario_id', backref='destinatario', lazy=True)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    especialidade = db.Column(db.String(50), nullable=False)
    data_agendamento = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, confirmado, cancelado, realizado
    descricao = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(30), default='informacao')  # informacao, lembrete, alerta
    prioridade = db.Column(db.String(20), default='normal')  # baixa, normal, alta, urgente
    lida = db.Column(db.Boolean, default=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo_mensagem = db.Column(db.String(20), default='texto')  # texto, arquivo, audio
    arquivo_url = db.Column(db.String(200))
    lida = db.Column(db.Boolean, default=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
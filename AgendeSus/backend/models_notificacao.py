# models/models_notificacao.py
# AgendeSUS DF - Models para Sistema de Notificações

from app_init import db
from datetime import datetime

class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'))
    
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), default='info')  # 'info', 'lembrete', 'cancelamento', 'confirmacao'
    prioridade = db.Column(db.String(20), default='normal')  # 'baixa', 'normal', 'alta', 'urgente'
    
    lida = db.Column(db.Boolean, default=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    data_leitura = db.Column(db.DateTime)
    
    # Campos para notificações por email/SMS
    enviado_email = db.Column(db.Boolean, default=False)
    enviado_sms = db.Column(db.Boolean, default=False)
    tentativas_envio = db.Column(db.Integer, default=0)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='notificacoes')
    agendamento = db.relationship('Agendamento', backref='notificacoes_relacionadas')
    
    def __repr__(self):
        return f'<Notificacao {self.id}: {self.titulo}>'
    
    def marcar_como_lida(self):
        """Marca a notificação como lida"""
        self.lida = True
        self.data_leitura = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Converte para dicionário para JSON"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'mensagem': self.mensagem,
            'tipo': self.tipo,
            'prioridade': self.prioridade,
            'lida': self.lida,
            'data_envio': self.data_envio.strftime('%d/%m/%Y %H:%M') if self.data_envio else None,
            'data_leitura': self.data_leitura.strftime('%d/%m/%Y %H:%M') if self.data_leitura else None
        }

class TemplateNotificacao(db.Model):
    __tablename__ = 'templates_notificacao'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    titulo_template = db.Column(db.String(200), nullable=False)
    mensagem_template = db.Column(db.Text, nullable=False)
    
    # Templates para diferentes canais
    template_email = db.Column(db.Text)
    template_sms = db.Column(db.Text)
    
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TemplateNotificacao {self.nome}>'

class ConfiguracaoNotificacao(db.Model):
    __tablename__ = 'configuracoes_notificacao'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Preferências de notificação
    receber_email = db.Column(db.Boolean, default=True)
    receber_sms = db.Column(db.Boolean, default=False)
    receber_push = db.Column(db.Boolean, default=True)
    
    # Tipos de notificação
    lembretes_cirurgia = db.Column(db.Boolean, default=True)
    confirmacoes_agendamento = db.Column(db.Boolean, default=True)
    cancelamentos = db.Column(db.Boolean, default=True)
    vagas_liberadas = db.Column(db.Boolean, default=True)
    
    # Timing dos lembretes
    lembrete_24h = db.Column(db.Boolean, default=True)
    lembrete_2h = db.Column(db.Boolean, default=True)
    
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='config_notificacao', uselist=False)
    
    def __repr__(self):
        return f'<ConfiguracaoNotificacao User:{self.usuario_id}>'
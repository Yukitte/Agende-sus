# models.py

from flask_sqlalchemy import SQLAlchemy
# Removido: from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime 

db = SQLAlchemy() 

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False) # Aumentei para 255, pois bcrypt gera hashes mais longos
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    telefone = db.Column(db.String(11), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    cartao_sus = db.Column(db.String(15), unique=True, nullable=False)
    tipo = db.Column(db.String(20), default='paciente', nullable=False) # paciente ou admin
    genero = db.Column(db.String(20), nullable=True)
    endereco_completo = db.Column(db.String(255), nullable=True) # Aumentei para 255

    # Removidos os métodos set_password e check_password daqui.
    # O hashing e verificação serão feitos DIRETAMENTE no app.py usando a instância 'bcrypt'
    # que é configurada com o aplicativo Flask.

class Medico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    crm = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(11), nullable=False)
    especialidade_id = db.Column(db.Integer, db.ForeignKey('especialidade.id'), nullable=False)
    especialidade = db.relationship('Especialidade', backref='medicos', lazy=True)

class Especialidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

class Horario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False) # Confirme se você quer db.Time ou String
    disponivel = db.Column(db.Boolean, default=True, nullable=False)
    medico = db.relationship('Medico', backref='horarios', lazy=True)

class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horario.id'), nullable=False)
    status = db.Column(db.String(20), default='agendada', nullable=False) 
    data_agendamento = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) 
    
    usuario = db.relationship('Usuario', backref='consultas', lazy=True)
    medico = db.relationship('Medico', backref='consultas', lazy=True)
    horario = db.relationship('Horario', backref='consulta', uselist=False, lazy=True)
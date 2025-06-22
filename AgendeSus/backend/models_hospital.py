"""
Modelo para Hospital - AgendeSUS DF
"""

from app_init import db
from datetime import datetime


class Hospital(db.Model):
    __tablename__ = 'hospitais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.String(15))
    especialidades = db.Column(db.Text)  # JSON string com especialidades
    capacidade_cirurgica = db.Column(db.Integer, default=10)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    profissionais = db.relationship('ProfissionalSaude', backref='hospital', lazy=True)
    agendamentos = db.relationship('Agendamento', backref='hospital', lazy=True)
    
    def __repr__(self):
        return f'<Hospital {self.nome}>'
    
    def to_dict(self):
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'especialidades': self.especialidades,
            'capacidade_cirurgica': self.capacidade_cirurgica,
            'ativo': self.ativo
        }
    
    @staticmethod
    def get_hospitais_ativos():
        """Retorna todos os hospitais ativos"""
        return Hospital.query.filter_by(ativo=True).all()
    
    def get_especialidades_list(self):
        """Retorna lista de especialidades do hospital"""
        try:
            import json
            return json.loads(self.especialidades) if self.especialidades else []
        except:
            return []
    
    def set_especialidades_list(self, especialidades_list):
        """Define lista de especialidades do hospital"""
        import json
        self.especialidades = json.dumps(especialidades_list)
    
    def verificar_capacidade(self, data_cirurgia):
        """Verifica se há capacidade disponível para determinada data"""
        from models.agendamento import Agendamento
        
        agendamentos_data = Agendamento.query.filter(
            Agendamento.hospital_id == self.id,
            Agendamento.data_cirurgia == data_cirurgia,
            Agendamento.status.in_(['agendado', 'confirmado'])
        ).count()
        
        return agendamentos_data < self.capacidade_cirurgica

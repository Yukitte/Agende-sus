"""
Modelo para Profissional de Saúde - AgendeSUS DF
"""

from app_init import db
from datetime import datetime


class ProfissionalSaude(db.Model):
    __tablename__ = 'profissionais_saude'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    registro_profissional = db.Column(db.String(20), unique=True, nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitais.id'))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    equipes = db.relationship('EquipeCirurgia', secondary='equipe_membros', back_populates='membros')
    agendamentos_responsavel = db.relationship('Agendamento', backref='profissional_responsavel', lazy=True)
    
    def __repr__(self):
        return f'<ProfissionalSaude {self.usuario.nome}>'
    
    def to_dict(self):
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.usuario.nome,
            'registro_profissional': self.registro_profissional,
            'especialidade': self.especialidade,
            'hospital': self.hospital.nome if self.hospital else None,
            'ativo': self.ativo
        }
    
    @staticmethod
    def get_por_especialidade(especialidade):
        """Retorna profissionais por especialidade"""
        return ProfissionalSaude.query.filter_by(
            especialidade=especialidade, 
            ativo=True
        ).all()
    
    @staticmethod
    def get_por_hospital(hospital_id):
        """Retorna profissionais por hospital"""
        return ProfissionalSaude.query.filter_by(
            hospital_id=hospital_id,
            ativo=True
        ).all()
    
    def get_agendamentos_periodo(self, data_inicio, data_fim):
        """Retorna agendamentos do profissional em um período"""
        from models_agendamento import Agendamento
        
        return Agendamento.query.filter(
            Agendamento.profissional_id == self.id,
            Agendamento.data_cirurgia.between(data_inicio, data_fim)
        ).all()


class EquipeCirurgia(db.Model):
    __tablename__ = 'equipes_cirurgia'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativa = db.Column(db.Boolean, default=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitais.id'))
    
    # Relacionamentos
    membros = db.relationship('ProfissionalSaude', secondary='equipe_membros', back_populates='equipes')
    agendamentos = db.relationship('Agendamento', backref='equipe', lazy=True)
    
    def __repr__(self):
        return f'<EquipeCirurgia {self.nome}>'
    
    def to_dict(self):
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'especialidade': self.especialidade,
            'total_membros': len(self.membros),
            'ativa': self.ativa
        }
    
    def adicionar_membro(self, profissional):
        """Adiciona membro à equipe"""
        if profissional not in self.membros:
            self.membros.append(profissional)
            return True
        return False
    
    def remover_membro(self, profissional):
        """Remove membro da equipe"""
        if profissional in self.membros:
            self.membros.remove(profissional)
            return True
        return False


# Tabela de associação para equipes e membros
equipe_membros = db.Table('equipe_membros',
    db.Column('equipe_id', db.Integer, db.ForeignKey('equipes_cirurgia.id'), primary_key=True),
    db.Column('profissional_id', db.Integer, db.ForeignKey('profissionais_saude.id'), primary_key=True),
    db.Column('data_adicao', db.DateTime, default=datetime.utcnow)
)

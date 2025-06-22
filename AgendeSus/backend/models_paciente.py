"""
Modelo para Paciente - AgendeSUS DF
"""

from app_init import db
from datetime import datetime, date


class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cartao_sus = db.Column(db.String(15), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.Text)
    historico_medico = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy=True)
    lista_espera = db.relationship('ListaEspera', backref='paciente', lazy=True)
    
    def __repr__(self):
        return f'<Paciente {self.usuario.nome}>'
    
    def to_dict(self):
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.usuario.nome,
            'email': self.usuario.email,
            'cartao_sus': self.cartao_sus,
            'data_nascimento': self.data_nascimento.strftime('%d/%m/%Y'),
            'idade': self.calcular_idade(),
            'endereco': self.endereco,
            'ativo': self.ativo
        }
    
    def calcular_idade(self):
        """Calcula idade do paciente"""
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
    
    def get_agendamentos_ativos(self):
        """Retorna agendamentos ativos do paciente"""
        from models.agendamento import Agendamento
        
        return Agendamento.query.filter(
            Agendamento.paciente_id == self.id,
            Agendamento.status.in_(['agendado', 'confirmado'])
        ).order_by(Agendamento.data_cirurgia).all()
    
    def get_historico_cirurgias(self):
        """Retorna histórico de cirurgias realizadas"""
        from models.agendamento import Agendamento
        
        return Agendamento.query.filter(
            Agendamento.paciente_id == self.id,
            Agendamento.status == 'realizado'
        ).order_by(Agendamento.data_cirurgia.desc()).all()
    
    def get_lista_espera_ativa(self):
        """Retorna itens da lista de espera ativos"""
        from models.lista_espera import ListaEspera
        
        return ListaEspera.query.filter(
            ListaEspera.paciente_id == self.id,
            ListaEspera.ativa == True
        ).order_by(ListaEspera.prioridade.desc(), ListaEspera.data_entrada).all()
    
    def tem_agendamento_conflitante(self, data_cirurgia):
        """Verifica se paciente tem agendamento conflitante"""
        from models.agendamento import Agendamento
        
        # Verifica se há agendamento no mesmo dia
        inicio_dia = data_cirurgia.replace(hour=0, minute=0, second=0, microsecond=0)
        fim_dia = data_cirurgia.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conflito = Agendamento.query.filter(
            Agendamento.paciente_id == self.id,
            Agendamento.data_cirurgia.between(inicio_dia, fim_dia),
            Agendamento.status.in_(['agendado', 'confirmado'])
        ).first()
        
        return conflito is not None
    
    def adicionar_historico_medico(self, texto):
        """Adiciona entrada ao histórico médico"""
        if self.historico_medico:
            self.historico_medico += f"\n{datetime.now().strftime('%d/%m/%Y %H:%M')}: {texto}"
        else:
            self.historico_medico = f"{datetime.now().strftime('%d/%m/%Y %H:%M')}: {texto}"
    
    @staticmethod
    def buscar_por_cartao_sus(cartao_sus):
        """Busca paciente por cartão SUS"""
        return Paciente.query.filter_by(cartao_sus=cartao_sus, ativo=True).first()
    
    @staticmethod
    def buscar_por_cpf(cpf):
        """Busca paciente por CPF"""
        from models.usuarios import Usuario
        
        usuario = Usuario.query.filter_by(cpf=cpf, tipo_usuario='paciente').first()
        if usuario:
            return usuario.paciente
        return None
    
    def validar_dados(self):
        """Valida dados do paciente"""
        errors = []
        
        if not self.cartao_sus or len(self.cartao_sus) != 15:
            errors.append("Cartão SUS deve ter 15 dígitos")
        
        if not self.data_nascimento:
            errors.append("Data de nascimento é obrigatória")
        elif self.data_nascimento > date.today():
            errors.append("Data de nascimento não pode ser futura")
        
        # Validar idade mínima (0 anos) e máxima (120 anos)
        idade = self.calcular_idade()
        if idade < 0 or idade > 120:
            errors.append("Idade inválida")
        
        return errors

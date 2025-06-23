"""
AgendeSUS DF - Modelo de Pacientes
Definição da estrutura de dados específica para pacientes
"""

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Paciente(db.Model):
    """Modelo específico para pacientes do sistema"""
    
    __tablename__ = 'pacientes'
    
    # Chave primária
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    
    # Dados do SUS
    cartao_sus = db.Column(db.String(15), unique=True, nullable=False, index=True)
    numero_prontuario = db.Column(db.String(20), unique=True, index=True)
    
    # Dados pessoais específicos
    data_nascimento = db.Column(db.Date, nullable=False)
    nome_mae = db.Column(db.String(100))
    nome_pai = db.Column(db.String(100))
    estado_civil = db.Column(db.String(20))  # 'solteiro', 'casado', 'viuvo', 'divorciado'
    profissao = db.Column(db.String(100))
    escolaridade = db.Column(db.String(50))
    
    # Endereço detalhado
    cep = db.Column(db.String(8))
    endereco = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(50))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    ponto_referencia = db.Column(db.String(200))
    
    # Contatos de emergência
    contato_emergencia_nome = db.Column(db.String(100))
    contato_emergencia_telefone = db.Column(db.String(15))
    contato_emergencia_parentesco = db.Column(db.String(50))
    
    # Dados médicos
    tipo_sanguineo = db.Column(db.String(3))  # 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
    peso = db.Column(db.Float)  # em kg
    altura = db.Column(db.Float)  # em metros
    
    # Histórico médico
    historico_medico = db.Column(db.Text)
    alergias = db.Column(db.Text)  # JSON string
    medicamentos_uso_continuo = db.Column(db.Text)  # JSON string
    cirurgias_anteriores = db.Column(db.Text)  # JSON string
    historico_familiar = db.Column(db.Text)
    
    # Condições especiais
    possui_convenio = db.Column(db.Boolean, default=False)
    convenio_nome = db.Column(db.String(100))
    convenio_numero = db.Column(db.String(50))
    
    # Necessidades especiais
    necessita_acompanhante = db.Column(db.Boolean, default=False)
    necessita_transporte = db.Column(db.Boolean, default=False)
    tem_deficiencia = db.Column(db.Boolean, default=False)
    tipo_deficiencia = db.Column(db.String(200))
    observacoes_especiais = db.Column(db.Text)
    
    # Status e controle
    status_ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultima_consulta = db.Column(db.DateTime)
    
    # Dados de auditoria
    cadastrado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy='dynamic')
    lista_espera = db.relationship('ListaEspera', backref='paciente', lazy='dynamic')
    avaliacoes = db.relationship('AvaliacaoAtendimento', backref='paciente', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Paciente, self).__init__(**kwargs)
        if not self.numero_prontuario:
            self.numero_prontuario = self.gerar_numero_prontuario()
    
    def __repr__(self):
        return f'<Paciente {self.usuario.nome} - SUS: {self.cartao_sus}>'
    
    # Métodos de propriedades calculadas
    def get_idade(self):
        """Calcula a idade do paciente"""
        if not self.data_nascimento:
            return None
        
        hoje = date.today()
        idade = hoje.year - self.data_nascimento.year
        
        if hoje < self.data_nascimento.replace(year=hoje.year):
            idade -= 1
            
        return idade

# models/models_lista_espera.py
# AgendeSUS DF - Models para Sistema de Lista de Espera

from app_init import db
from datetime import datetime
from sqlalchemy import and_, or_

class ListaEspera(db.Model):
    __tablename__ = 'lista_espera'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitais.id'))
    
    # Informações da cirurgia
    especialidade = db.Column(db.String(100), nullable=False)
    tipo_cirurgia = db.Column(db.String(100), nullable=False)
    
    # Sistema de prioridade
    prioridade = db.Column(db.Integer, default=1)  # 1=baixa, 2=média, 3=alta, 4=urgente
    urgencia_medica = db.Column(db.Boolean, default=False)
    
    # Critérios de priorização
    idade_paciente = db.Column(db.Integer)
    tempo_espera_dias = db.Column(db.Integer, default=0)
    gravidade_caso = db.Column(db.String(20), default='eletivo')  # 'eletivo', 'urgente', 'emergencial'
    
    # Preferências do paciente
    disponibilidade_manha = db.Column(db.Boolean, default=True)
    disponibilidade_tarde = db.Column(db.Boolean, default=True)
    disponibilidade_noite = db.Column(db.Boolean, default=False)
    
    # Controle de status
    ativa = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='aguardando')  # 'aguardando', 'contatado', 'agendado', 'cancelado'
    
    # Datas importantes
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    data_ultimo_contato = db.Column(db.DateTime)
    data_limite_resposta = db.Column(db.DateTime)
    data_saida = db.Column(db.DateTime)
    
    # Observações
    observacoes = db.Column(db.Text)
    observacoes_medicas = db.Column(db.Text)
    
    # Relacionamentos
    paciente = db.relationship('Paciente', backref='filas_espera')
    hospital = db.relationship('Hospital', backref='filas_espera')
    historico = db.relationship('HistoricoListaEspera', backref='lista_espera', lazy=True)
    
    def __repr__(self):
        return f'<ListaEspera {self.id}: {self.paciente.usuario.nome} - {self.especialidade}>'
    
    @property
    def posicao_fila(self):
        """Calcula a posição na fila baseada na prioridade e tempo de espera"""
        anteriores = ListaEspera.query.filter(
            and_(
                ListaEspera.especialidade == self.especialidade,
                ListaEspera.ativa == True,
                ListaEspera.id != self.id,
                or_(
                    ListaEspera.prioridade > self.prioridade,
                    and_(
                        ListaEspera.prioridade == self.prioridade,
                        ListaEspera.data_entrada < self.data_entrada
                    )
                )
            )
        ).count()
        
        return anteriores + 1
    
    @property
    def tempo_espera_atual(self):
        """Calcula o tempo de espera atual em dias"""
        if self.data_saida:
            return (self.data_saida - self.data_entrada).days
        return (datetime.utcnow() - self.data_entrada).days
    
    def calcular_prioridade(self):
        """Calcula a prioridade baseada em diversos fatores"""
        score = 0
        
        # Prioridade base
        score += self.prioridade * 10
        
        # Urgência médica
        if self.urgencia_medica:
            score += 50
        
        # Gravidade do caso
        if self.gravidade_caso == 'urgente':
            score += 30
        elif self.gravidade_caso == 'emergencial':
            score += 100
        
        # Idade (prioridade para idosos e crianças)
        if self.idade_paciente:
            if self.idade_paciente >= 65:
                score += 15
            elif self.idade_paciente <= 12:
                score += 10
        
        # Tempo de espera (1 ponto por dia)
        score += self.tempo_espera_atual
        
        return score
    
    def atualizar_tempo_espera(self):
        """Atualiza o campo tempo_espera_dias"""
        self.tempo_espera_dias = self.tempo_espera_atual
        db.session.commit()
    
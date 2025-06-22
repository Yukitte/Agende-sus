"""
Modelo para Chat - AgendeSUS DF
"""

from app_init import db
from datetime import datetime
from sqlalchemy import desc


class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=False)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    lida = db.Column(db.Boolean, default=False)
    tipo_mensagem = db.Column(db.String(20), default='texto')  # 'texto', 'arquivo', 'imagem'
    arquivo_url = db.Column(db.String(255))  # URL do arquivo anexado
    
    # Relacionamentos
    agendamento = db.relationship('Agendamento', backref='mensagens_chat')
    remetente = db.relationship('Usuario', backref='mensagens_enviadas')
    
    def __repr__(self):
        return f'<Chat {self.id} - {self.remetente.nome}>'
    
    def to_dict(self):
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'agendamento_id': self.agendamento_id,
            'remetente_id': self.remetente_id,
            'remetente_nome': self.remetente.nome,
            'remetente_tipo': self.remetente.tipo_usuario,
            'mensagem': self.mensagem,
            'data_envio': self.data_envio.strftime('%d/%m/%Y %H:%M'),
            'lida': self.lida,
            'tipo_mensagem': self.tipo_mensagem,
            'arquivo_url': self.arquivo_url
        }
    
    @staticmethod
    def get_mensagens_agendamento(agendamento_id, limit=50):
        """Retorna mensagens de um agendamento"""
        return Chat.query.filter_by(agendamento_id=agendamento_id)\
                        .order_by(Chat.data_envio)\
                        .limit(limit)\
                        .all()
    
    @staticmethod
    def get_mensagens_nao_lidas(usuario_id, agendamento_id):
        """Retorna mensagens não lidas para um usuário"""
        return Chat.query.filter(
            Chat.agendamento_id == agendamento_id,
            Chat.remetente_id != usuario_id,
            Chat.lida == False
        ).all()
    
    @staticmethod
    def marcar_como_lidas(agendamento_id, usuario_id):
        """Marca mensagens como lidas para um usuário"""
        try:
            Chat.query.filter(
                Chat.agendamento_id == agendamento_id,
                Chat.remetente_id != usuario_id,
                Chat.lida == False
            ).update({'lida': True})
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def criar_mensagem(agendamento_id, remetente_id, mensagem, tipo_mensagem='texto', arquivo_url=None):
        """Cria nova mensagem no chat"""
        try:
            nova_mensagem = Chat(
                agendamento_id=agendamento_id,
                remetente_id=remetente_id,
                mensagem=mensagem,
                tipo_mensagem=tipo_mensagem,
                arquivo_url=arquivo_url
            )
            
            db.session.add(nova_mensagem)
            db.session.commit()
            
            return nova_mensagem
        except Exception as e:
            db.session.rollback()
            return None
    
    def pode_editar(self, usuario_id):
        """Verifica se usuário pode editar a mensagem"""
        # Só pode editar próprias mensagens e dentro de 15 minutos
        if self.remetente_id != usuario_id:
            return False
        
        limite_edicao = datetime.utcnow() - timedelta(minutes=15)
        return self.data_envio > limite_edicao
    
    def pode_deletar(self, usuario_id):
        """Verifica se usuário pode deletar a mensagem"""
        # Só pode deletar próprias mensagens
        return self.remetente_id == usuario_id
    
    @staticmethod
    def get_conversas_usuario(usuario_id):
        """Retorna todas as conversas de um usuário"""
        from models.agendamento import Agendamento
        from models.usuarios import Usuario
        
        # Buscar agendamentos onde o usuário participa
        subquery = db.session.query(Chat.agendamento_id)\
                            .filter(Chat.remetente_id == usuario_id)\
                            .subquery()
        
        # Buscar últimas mensagens de cada conversa
        conversas = db.session.query(
            Chat.agendamento_id,
            Chat.mensagem,
            Chat.data_envio,
            Agendamento.paciente_id,
            Agendamento.tipo_cirurgia
        ).join(Agendamento)\
         .filter(Chat.agendamento_id.in_(subquery))\
         .order_by(desc(Chat.data_envio))\
         .all()
        
        return conversas
    
    @staticmethod
    def get_estatisticas_chat(agendamento_id):
        """Retorna estatísticas do chat"""
        total_mensagens = Chat.query.filter_by(agendamento_id=agendamento_id).count()
        
        mensagens_por_tipo = db.session.query(
            Chat.tipo_mensagem,
            db.func.count(Chat.id).label('total')
        ).filter_by(agendamento_id=agendamento_id)\
         .group_by(Chat.tipo_mensagem)\
         .all()
        
        primeira_mensagem = Chat.query.filter_by(agendamento_id=agendamento_id)\
                                    .order_by(Chat.data_envio)\
                                    .first()
        
        ultima_mensagem = Chat.query.filter_by(agendamento_id=agendamento_id)\
                                  .order_by(desc(Chat.data_envio))\
                                  .first()
        
        return {
            'total_mensagens': total_mensagens,
            'mensagens_por_tipo': dict(mensagens_por_tipo),
            'primeira_mensagem': primeira_mensagem.data_envio if primeira_mensagem else None,
            'ultima_mensagem': ultima_mensagem.data_envio if ultima_mensagem else None
        }


class ChatArquivo(db.Model):
    __tablename__ = 'chat_arquivos'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    nome_original = db.Column(db.String(255), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tipo_arquivo = db.Column(db.String(50))
    tamanho = db.Column(db.Integer)
    url = db.Column(db.String(500), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    chat = db.relationship('Chat', backref='arquivos')
    
    def __repr__(self):
        return f'<ChatArquivo {self.nome_original}>'
    
    def to_dict(self):
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'nome_original': self.nome_original,
            'nome_arquivo': self.nome_arquivo,
            'tipo_arquivo': self.tipo_arquivo,
            'tamanho': self.tamanho,
            'url': self.url,
            'data_upload': self.data_upload.strftime('%d/%m/%Y %H:%M')
        }
    
    def formatar_tamanho(self):
        """Formata tamanho do arquivo para exibição"""
        if not self.tamanho:
            return "N/A"
        
        if self.tamanho < 1024:
            return f"{self.tamanho} bytes"
        elif self.tamanho < 1024 * 1024:
            return f"{self.tamanho / 1024:.1f} KB"
        else:
            return f"{self.tamanho / (1024 * 1024):.1f} MB"

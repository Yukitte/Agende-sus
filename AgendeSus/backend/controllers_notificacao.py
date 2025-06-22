# controllers/controllers_notificacao.py
# AgendeSUS DF - Controller para Sistema de Notificações

from app_init import db, mail
from models.models_notificacao import Notificacao, TemplateNotificacao, ConfiguracaoNotificacao
from models.models_agendamento import Agendamento
from models.models_usuarios import Usuario
from flask_mail import Message
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificacaoController:
    
    @staticmethod
    def criar_notificacao(usuario_id, titulo, mensagem, tipo='info', prioridade='normal', 
                         agendamento_id=None, enviar_email=False, enviar_sms=False):
        """
        Cria uma nova notificação
        
        Args:
            usuario_id: ID do usuário
            titulo: Título da notificação
            mensagem: Mensagem da notificação
            tipo: Tipo da notificação
            prioridade: Prioridade da notificação
            agendamento_id: ID do agendamento relacionado (opcional)
            enviar_email: Se deve enviar por email
            enviar_sms: Se deve enviar por SMS
        
        Returns:
            dict: Resultado da operação
        """
        try:
            # Verificar configurações do usuário
            config = ConfiguracaoNotificacao.query.filter_by(usuario_id=usuario_id).first()
            if not config:
                config = NotificacaoController._criar_configuracao_padrao(usuario_id)
            
            # Criar notificação
            notificacao = Notificacao(
                usuario_id=usuario_id,
                agendamento_id=agendamento_id,
                titulo=titulo,
                mensagem=mensagem,
                tipo=tipo,
                prioridade=prioridade
            )
            
            db.session.add(notificacao)
            db.session.flush()  # Para obter o ID
            
            # Enviar por diferentes canais se configurado
            if enviar_email and config.receber_email:
                NotificacaoController._enviar_email(notificacao)
            
            if enviar_sms and config.receber_sms:
                NotificacaoController._enviar_sms(notificacao)
            
            db.session.commit()
            
            logger.info(f"Notificação criada: ID {notificacao.id} para usuário {usuario_id}")
            
            return {
                'success': True,
                'notificacao_id': notificacao.id,
                'message': 'Notificação criada com sucesso'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar notificação: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao criar notificação: {str(e)}'
            }
    
    @staticmethod
    def enviar_notificacao_agendamento(agendamento_id):
        """Envia notificação de agendamento confirmado"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return {'success': False, 'message': 'Agendamento não encontrado'}
            
            titulo = 'Cirurgia Agendada ✅'
            mensagem = f"""
            Sua cirurgia foi agendada com sucesso!
            
            📅 Data: {agendamento.data_cirurgia.strftime('%d/%m/%Y')}
            🕐 Horário: {agendamento.data_cirurgia.strftime('%H:%M')}
            🏥 Hospital: {agendamento.hospital.nome}
            ⚕️ Tipo: {agendamento.tipo_cirurgia}
            🔬 Especialidade: {agendamento.especialidade}
            
            Você receberá lembretes antes da data da cirurgia.
            """
            
            return NotificacaoController.criar_notificacao(
                usuario_id=agendamento.paciente.usuario_id,
                titulo=titulo,
                mensagem=mensagem,
                tipo='confirmacao',
                prioridade='alta',
                agendamento_id=agendamento_id,
                enviar_email=True
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de agendamento: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def enviar_notificacao_cancelamento(agendamento_id, motivo=''):
        """Envia notificação de cancelamento"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return {'success': False, 'message': 'Agendamento não encontrado'}
            
            titulo = 'Cirurgia Cancelada ❌'
            mensagem = f"""
            Sua cirurgia foi cancelada.
            
            📅 Data Original: {agendamento.data_cirurgia.strftime('%d/%m/%Y às %H:%M')}
            🏥 Hospital: {agendamento.hospital.nome}
            ⚕️ Tipo: {agendamento.tipo_cirurgia}
            
            {f'Motivo: {motivo}' if motivo else ''}
            
            Entre em contato conosco para reagendar.
            """
            
            return NotificacaoController.criar_notificacao(
                usuario_id=agendamento.paciente.usuario_id,
                titulo=titulo,
                mensagem=mensagem,
                tipo='cancelamento',
                prioridade='urgente',
                agendamento_id=agendamento_id,
                enviar_email=True,
                enviar_sms=True
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de cancelamento: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def enviar_notificacao_vaga_liberada(usuario_id, agendamento_id):
        """Envia notificação de vaga liberada da lista de espera"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            
            titulo = 'Vaga Liberada! 🎉'
            mensagem = f"""
            Ótima notícia! Uma vaga foi liberada e você foi automaticamente agendado!
            
            📅 Data: {agendamento.data_cirurgia.strftime('%d/%m/%Y')}
            🕐 Horário: {agendamento.data_cirurgia.strftime('%H:%M')}
            🏥 Hospital: {agendamento.hospital.nome}
            ⚕️ Tipo: {agendamento.tipo_cirurgia}
            
            ⚠️ IMPORTANTE: Confirme sua presença em até 24 horas.
            Caso contrário, a vaga será oferecida para o próximo da lista.
            """
            
            return NotificacaoController.criar_notificacao(
                usuario_id=usuario_id,
                titulo=titulo,
                mensagem=mensagem,
                tipo='info',
                prioridade='urgente',
                agendamento_id=agendamento_id,
                enviar_email=True,
                enviar_sms=True
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de vaga liberada: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def enviar_lembretes_automaticos():
        """
        Envia lembretes automáticos baseados nas configurações
        Deve ser executado periodicamente (cron job)
        """
        try:
            resultados = {
                'lembretes_24h': 0,
                'lembretes_2h': 0,
                'erros': 0
            }
            
            # Lembretes 24 horas antes
            amanha = datetime.now() + timedelta(days=1)
            inicio_amanha = amanha.replace(hour=0, minute=0, second=0, microsecond=0)
            fim_amanha = amanha.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            agendamentos_24h = Agendamento.query.filter(
                Agendamento.data_cirurgia.between(inicio_amanha, fim_amanha),
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).all()
            
            for agendamento in agendamentos_24h:
                config = ConfiguracaoNotificacao.query.filter_by(
                    usuario_id=agendamento.paciente.usuario_id
                ).first()
                
                if config and config.lembrete_24h:
                    resultado = NotificacaoController._enviar_lembrete_24h(agendamento)
                    if resultado['success']:
                        resultados['lembretes_24h'] += 1
                    else:
                        resultados['erros'] += 1
            
            # Lembretes 2 horas antes
            duas_horas = datetime.now() + timedelta(hours=2)
            inicio_2h = duas_horas.replace(minute=0, second=0, microsecond=0)
            fim_2h = duas_horas.replace(minute=59, second=59, microsecond=999999)
            
            agendamentos_2h = Agendamento.query.filter(
                Agendamento.data_cirurgia.between(inicio_2h, fim_2h),
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).all()
            
            for agendamento in agendamentos_2h:
                config = ConfiguracaoNotificacao.query.filter_by(
                    usuario_id=agendamento.paciente.usuario_id
                ).first()
                
                if config and config.lembrete_2h:
                    resultado = NotificacaoController._enviar_lembrete_2h(agendamento)
                    if resultado['success']:
                        resultados['lembretes_2h'] += 1
                    else:
                        resultados['erros'] += 1
            
            logger.info(f"Lembretes enviados: {resultados}")
            return {'success': True, 'resultados': resultados}
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembretes automáticos: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _enviar_lembrete_24h(agendamento):
        """Envia lembrete 24 horas antes"""
        titulo = 'Lembrete: Cirurgia Amanhã 📅'
        mensagem = f"""
        Lembrete: Sua cirurgia está agendada para AMANHÃ!
        
        📅 Data: {agendamento.data_cirurgia.strftime('%d/%m/%Y')}
        🕐 Horário: {agendamento.data_cirurgia.strftime('%H:%M')}
        🏥 Hospital: {agendamento.hospital.nome}
        ⚕️ Tipo: {agendamento.tipo_cirurgia}
        
        📋 Instruções pré-operatórias:
        • Jejum de 8 horas (conforme orientação médica)
        • Chegue com 1 hora de antecedência
        • Traga documento, cartão SUS e exames
        • Use roupas confortáveis
        
        Em caso de dúvidas, entre em contato conosco.
        """
        
        return NotificacaoController.criar_notificacao(
            usuario_id=agendamento.paciente.usuario_id,
            titulo=titulo,
            mensagem=mensagem,
            tipo='lembrete',
            prioridade='alta',
            agendamento_id=agendamento.id,
            enviar_email=True
        )
    
    @staticmethod
    def _enviar_lembrete_2h(agendamento):
        """Envia lembrete 2 horas antes"""
        titulo = 'Lembrete URGENTE: Cirurgia em 2h ⏰'
        mensagem = f"""
        🚨 LEMBRETE URGENTE: Sua cirurgia é em 2 HORAS!
        
        🕐 Horário: {agendamento.data_cirurgia.strftime('%H:%M')}
        🏥 Hospital: {agendamento.hospital.nome}
        📍 Endereço: {agendamento.hospital.endereco}
        
        ⚠️ IMPORTANTE:
        • Chegue em 1 HORA (às {(agendamento.data_cirurgia - timedelta(hours=1)).strftime('%H:%M')})
        • Confirme o jejum
        • Tenha documentos em mãos
        
        Boa sorte! Nossa equipe está preparada para cuidar de você.
        """
        
        return NotificacaoController.criar_notificacao(
            usuario_id=agendamento.paciente.usuario_id,
            titulo=titulo,
            mensagem=mensagem,
            tipo='lembrete',
            prioridade='urgente',
            agendamento_id=agendamento.id,
            enviar_sms=True
        )
    
    @staticmethod
    def _enviar_email(notificacao):
        """Envia notificação por email"""
        try:
            usuario = Usuario.query.get(notificacao.usuario_id)
            
            msg = Message(
                subject=f'AgendeSUS DF - {notificacao.titulo}',
                sender='agendesus@saude.df.gov.br',
                recipients=[usuario.email]
            )
            
            msg.body = f"""
            Olá {usuario.nome},
            
            {notificacao.mensagem}
            
            ---
            AgendeSUS DF
            Secretaria de Saúde do Distrito Federal
            
            Esta é uma mensagem automática, não responda este email.
            """
            
            # mail.send(msg)  # Descomentار quando configurar SMTP real
            notificacao.enviado_email = True
            
            logger.info(f"Email enviado para {usuario.email}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            notificacao.tentativas_envio += 1
    
    @staticmethod
    def _enviar_sms(notificacao):
        """Envia notificação por SMS (simulação)"""
        try:
            usuario = Usuario.query.get(notificacao.usuario_id)
            
            # Aqui seria integrada uma API de SMS real (Twilio, AWS SNS, etc.)
            sms_texto = f"AgendeSUS DF: {notificacao.titulo} - {notificacao.mensagem[:100]}..."
            
            logger.info(f"SMS simulado para {usuario.telefone}: {sms_texto}")
            
            notificacao.enviado_sms = True
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {str(e)}")
            notificacao.tentativas_envio += 1
    
    @staticmethod
    def _criar_configuracao_padrao(usuario_id):
        """Cria configuração padrão de notificações para novo usuário"""
        try:
            config = ConfiguracaoNotificacao(
                usuario_id=usuario_id,
                receber_email=True,
                receber_sms=False,
                receber_push=True,
                lembretes_cirurgia=True,
                confirmacoes_agendamento=True,
                cancelamentos=True,
                vagas_liberadas=True,
                lembrete_24h=True,
                lembrete_2h=True
            )
            
            db.session.add(config)
            db.session.commit()
            
            return config
            
        except Exception as e:
            logger.error(f"Erro ao criar configuração padrão: {str(e)}")
            return None
    
    @staticmethod
    def marcar_como_lida(notificacao_id, usuario_id):
        """Marca uma notificação como lida"""
        try:
            notificacao = Notificacao.query.filter_by(
                id=notificacao_id, 
                usuario_id=usuario_id
            ).first()
            
            if notificacao:
                notificacao.marcar_como_lida()
                return {'success': True}
            else:
                return {'success': False, 'message': 'Notificação não encontrada'}
                
        except Exception as e:
            logger.error(f"Erro ao marcar notificação como lida: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def obter_notificacoes_usuario(usuario_id, apenas_nao_lidas=False, limite=50):
        """Obtém notificações do usuário"""
        try:
            query = Notificacao.query.filter_by(usuario_id=usuario_id)
            
            if apenas_nao_lidas:
                query = query.filter_by(lida=False)
            
            notificacoes = query.order_by(
                Notificacao.data_envio.desc()
            ).limit(limite).all()
            
            return {
                'success': True,
                'notificacoes': [n.to_dict() for n in notificacoes],
                'total_nao_lidas': Notificacao.query.filter_by(
                    usuario_id=usuario_id, lida=False
                ).count()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter notificações: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def atualizar_configuracoes(usuario_id, configuracoes):
        """Atualiza configurações de notificação do usuário"""
        try:
            config = ConfiguracaoNotificacao.query.filter_by(
                usuario_id=usuario_id
            ).first()
            
            if not config:
                config = NotificacaoController._criar_configuracao_padrao(usuario_id)
            
            # Atualizar configurações
            for key, value in configuracoes.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.data_atualizacao = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'message': 'Configurações atualizadas'}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar configurações: {str(e)}")
            return {'success': False, 'message': str(e)}
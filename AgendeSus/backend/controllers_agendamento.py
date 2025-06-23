# controllers/agendamento.py
from datetime import datetime, timedelta
from app_init import db
from models_agendamento import Agendamento, Hospital, ListaEspera, Notificacao
from models_usuarios import Paciente, ProfissionalSaude

class AgendamentoController:
    @staticmethod
    def criar_agendamento(dados):
        """Cria um novo agendamento de cirurgia"""
        try:
            # Verificar disponibilidade
            if not AgendamentoController.verificar_disponibilidade(
                dados['data_cirurgia'], dados['hospital_id']):
                return {'success': False, 'message': 'Horário não disponível'}
            
            # Validar data (não pode ser no passado)
            if dados['data_cirurgia'] <= datetime.now():
                return {'success': False, 'message': 'Data da cirurgia deve ser futura'}
            
            agendamento = Agendamento(
                paciente_id=dados['paciente_id'],
                hospital_id=dados['hospital_id'],
                data_cirurgia=dados['data_cirurgia'],
                tipo_cirurgia=dados['tipo_cirurgia'],
                especialidade=dados['especialidade'],
                urgencia=dados.get('urgencia', 'eletiva'),
                observacoes=dados.get('observacoes', '')
            )
            
            # Atribuir profissional se fornecido
            if dados.get('profissional_id'):
                agendamento.profissional_id = dados['profissional_id']
            
            # Atribuir equipe se fornecida
            if dados.get('equipe_id'):
                agendamento.equipe_id = dados['equipe_id']
            
            db.session.add(agendamento)
            db.session.commit()
            
            # Enviar notificação
            NotificacaoController.enviar_notificacao_agendamento(agendamento.id)
            
            return {'success': True, 'agendamento_id': agendamento.id}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def verificar_disponibilidade(data_cirurgia, hospital_id):
        """Verifica se há disponibilidade para a data/hospital"""
        try:
            agendamentos_existentes = Agendamento.query.filter(
                Agendamento.data_cirurgia == data_cirurgia,
                Agendamento.hospital_id == hospital_id,
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).count()
            
            hospital = Hospital.query.get(hospital_id)
            if not hospital:
                return False
                
            return agendamentos_existentes < hospital.capacidade_cirurgica
        except Exception as e:
            print(f"Erro ao verificar disponibilidade: {e}")
            return False
    
    @staticmethod
    def cancelar_agendamento(agendamento_id, motivo='', usuario_id=None):
        """Cancela um agendamento e libera vaga"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return {'success': False, 'message': 'Agendamento não encontrado'}
            
            # Verificar se pode cancelar
            if not agendamento.pode_cancelar:
                return {'success': False, 'message': 'Agendamento não pode ser cancelado'}
            
            agendamento.status = 'cancelado'
            if motivo:
                agendamento.observacoes = (agendamento.observacoes or '') + f'\nCancelado: {motivo}'
            
            db.session.commit()
            
            # Notificar cancelamento
            NotificacaoController.enviar_notificacao_cancelamento(agendamento_id, motivo)
            
            # Tentar realocar da lista de espera
            ListaEsperaController.processar_vaga_liberada(
                agendamento.especialidade, 
                agendamento.hospital_id,
                agendamento.data_cirurgia
            )
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def confirmar_agendamento(agendamento_id):
        """Confirma um agendamento"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return {'success': False, 'message': 'Agendamento não encontrado'}
            
            if agendamento.status != 'agendado':
                return {'success': False, 'message': 'Agendamento já foi processado'}
            
            agendamento.status = 'confirmado'
            db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def reagendar_cirurgia(agendamento_id, nova_data):
        """Reagenda uma cirurgia"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return {'success': False, 'message': 'Agendamento não encontrado'}
            
            # Verificar disponibilidade na nova data
            if not AgendamentoController.verificar_disponibilidade(nova_data, agendamento.hospital_id):
                return {'success': False, 'message': 'Nova data não disponível'}
            
            data_anterior = agendamento.data_cirurgia
            agendamento.data_cirurgia = nova_data
            agendamento.observacoes = (agendamento.observacoes or '') + f'\nReagendado de {data_anterior.strftime("%d/%m/%Y %H:%M")}'
            
            db.session.commit()
            
            # Notificar reagendamento
            NotificacaoController.enviar_notificacao_reagendamento(agendamento_id, data_anterior, nova_data)
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def buscar_agendamentos_paciente(paciente_id, status=None):
        """Busca agendamentos de um paciente"""
        try:
            query = Agendamento.query.filter_by(paciente_id=paciente_id)
            
            if status:
                query = query.filter_by(status=status)
            
            return query.order_by(Agendamento.data_cirurgia.desc()).all()
            
        except Exception as e:
            print(f"Erro ao buscar agendamentos: {e}")
            return []
    
    @staticmethod
    def buscar_agendamentos_profissional(profissional_id, data_inicio=None, data_fim=None):
        """Busca agendamentos de um profissional"""
        try:
            query = Agendamento.query.filter_by(profissional_id=profissional_id)
            
            if data_inicio:
                query = query.filter(Agendamento.data_cirurgia >= data_inicio)
            if data_fim:
                query = query.filter(Agendamento.data_cirurgia <= data_fim)
            
            return query.order_by(Agendamento.data_cirurgia).all()
            
        except Exception as e:
            print(f"Erro ao buscar agendamentos do profissional: {e}")
            return []
    
    @staticmethod
    def buscar_agendamentos_hospital(hospital_id, data_inicio=None, data_fim=None):
        """Busca agendamentos de um hospital"""
        try:
            query = Agendamento.query.filter_by(hospital_id=hospital_id)
            
            if data_inicio:
                query = query.filter(Agendamento.data_cirurgia >= data_inicio)
            if data_fim:
                query = query.filter(Agendamento.data_cirurgia <= data_fim)
            
            return query.order_by(Agendamento.data_cirurgia).all()
            
        except Exception as e:
            print(f"Erro ao buscar agendamentos do hospital: {e}")
            return []

class ListaEsperaController:
    @staticmethod
    def adicionar_lista_espera(paciente_id, especialidade, tipo_cirurgia, prioridade=1):
        """Adiciona paciente à lista de espera"""
        try:
            # Verificar se já está na lista para esta especialidade
            existe = ListaEspera.query.filter_by(
                paciente_id=paciente_id,
                especialidade=especialidade,
                ativa=True
            ).first()
            
            if existe:
                return {'success': False, 'message': 'Paciente já está na lista de espera para esta especialidade'}
            
            lista_espera = ListaEspera(
                paciente_id=paciente_id,
                especialidade=especialidade,
                tipo_cirurgia=tipo_cirurgia,
                prioridade=prioridade
            )
            
            db.session.add(lista_espera)
            db.session.commit()
            
            return {'success': True, 'lista_id': lista_espera.id}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def remover_lista_espera(lista_id):
        """Remove paciente da lista de espera"""
        try:
            lista = ListaEspera.query.get(lista_id)
            if not lista:
                return {'success': False, 'message': 'Item não encontrado na lista de espera'}
            
            lista.ativa = False
            db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def processar_vaga_liberada(especialidade, hospital_id, data_cirurgia):
        """Processa vaga liberada e tenta realocar da lista de espera"""
        try:
            # Buscar próximo na fila por prioridade e data de entrada
            proximo = ListaEspera.query.filter(
                ListaEspera.especialidade == especialidade,
                ListaEspera.ativa == True
            ).order_by(
                ListaEspera.prioridade.desc(), 
                ListaEspera.data_entrada
            ).first()
            
            if proximo:
                # Criar novo agendamento
                dados_agendamento = {
                    'paciente_id': proximo.paciente_id,
                    'hospital_id': hospital_id,
                    'data_cirurgia': data_cirurgia,
                    'tipo_cirurgia': proximo.tipo_cirurgia,
                    'especialidade': especialidade
                }
                
                resultado = AgendamentoController.criar_agendamento(dados_agendamento)
                
                if resultado['success']:
                    # Remover da lista de espera
                    proximo.ativa = False
                    db.session.commit()
                    
                    # Notificar paciente
                    NotificacaoController.enviar_notificacao_vaga_liberada(
                        proximo.paciente.usuario_id, resultado['agendamento_id']
                    )
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao processar vaga liberada: {e}")
            return False
    
    @staticmethod
    def buscar_lista_espera_paciente(paciente_id):
        """Busca itens da lista de espera de um paciente"""
        try:
            return ListaEspera.query.filter_by(
                paciente_id=paciente_id,
                ativa=True
            ).order_by(ListaEspera.data_entrada).all()
            
        except Exception as e:
            print(f"Erro ao buscar lista de espera: {e}")
            return []
    
    @staticmethod
    def buscar_lista_espera_especialidade(especialidade, limit=None):
        """Busca lista de espera por especialidade"""
        try:
            query = ListaEspera.query.filter_by(
                especialidade=especialidade,
                ativa=True
            ).order_by(
                ListaEspera.prioridade.desc(),
                ListaEspera.data_entrada
            )
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        except Exception as e:
            print(f"Erro ao buscar lista de espera por especialidade: {e}")
            return []

class NotificacaoController:
    @staticmethod
    def enviar_notificacao_agendamento(agendamento_id):
        """Envia notificação de agendamento confirmado"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return False
            
            notificacao = Notificacao(
                usuario_id=agendamento.paciente.usuario_id,
                agendamento_id=agendamento_id,
                titulo='Cirurgia Agendada',
                mensagem=f'Sua cirurgia de {agendamento.tipo_cirurgia} foi agendada para {agendamento.data_cirurgia.strftime("%d/%m/%Y às %H:%M")} no {agendamento.hospital.nome}.',
                tipo='info'
            )
            
            db.session.add(notificacao)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao enviar notificação de agendamento: {e}")
            return False
    
    @staticmethod
    def enviar_notificacao_cancelamento(agendamento_id, motivo=''):
        """Envia notificação de cancelamento"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return False
            
            mensagem = f'Sua cirurgia de {agendamento.tipo_cirurgia} agendada para {agendamento.data_cirurgia.strftime("%d/%m/%Y às %H:%M")} foi cancelada.'
            if motivo:
                mensagem += f' Motivo: {motivo}'
            
            notificacao = Notificacao(
                usuario_id=agendamento.paciente.usuario_id,
                agendamento_id=agendamento_id,
                titulo='Cirurgia Cancelada',
                mensagem=mensagem,
                tipo='cancelamento'
            )
            
            db.session.add(notificacao)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao enviar notificação de cancelamento: {e}")
            return False
    
    @staticmethod
    def enviar_notificacao_reagendamento(agendamento_id, data_anterior, nova_data):
        """Envia notificação de reagendamento"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return False
            
            notificacao = Notificacao(
                usuario_id=agendamento.paciente.usuario_id,
                agendamento_id=agendamento_id,
                titulo='Cirurgia Reagendada',
                mensagem=f'Sua cirurgia de {agendamento.tipo_cirurgia} foi reagendada de {data_anterior.strftime("%d/%m/%Y às %H:%M")} para {nova_data.strftime("%d/%m/%Y às %H:%M")}.',
                tipo='info'
            )
            
            db.session.add(notificacao)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao enviar notificação de reagendamento: {e}")
            return False
    
    @staticmethod
    def enviar_notificacao_vaga_liberada(usuario_id, agendamento_id):
        """Envia notificação de vaga liberada"""
        try:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return False
            
            notificacao = Notificacao(
                usuario_id=usuario_id,
                agendamento_id=agendamento_id,
                titulo='Vaga Liberada!',
                mensagem=f'Uma vaga foi liberada e você foi automaticamente agendado para {agendamento.data_cirurgia.strftime("%d/%m/%Y às %H:%M")}. Por favor, confirme sua cirurgia.',
                tipo='urgente'
            )
            
            db.session.add(notificacao)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao enviar notificação de vaga liberada: {e}")
            return False
    
    @staticmethod
    def enviar_lembretes_automaticos():
        """Envia lembretes automáticos 24h antes da cirurgia"""
        try:
            amanha = datetime.now() + timedelta(days=1)
            inicio_dia = amanha.replace(hour=0, minute=0, second=0, microsecond=0)
            fim_dia = amanha.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            agendamentos = Agendamento.query.filter(
                Agendamento.data_cirurgia.between(inicio_dia, fim_dia),
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).all()
            
            for agendamento in agendamentos:
                # Verificar se já foi enviado lembrete
                lembrete_existe = Notificacao.query.filter_by(
                    usuario_id=agendamento.paciente.usuario_id,
                    agendamento_id=agendamento.id,
                    tipo='lembrete'
                ).first()
                
                if not lembrete_existe:
                    notificacao = Notificacao(
                        usuario_id=agendamento.paciente.usuario_id,
                        agendamento_id=agendamento.id,
                        titulo='Lembrete de Cirurgia',
                        mensagem=f'Lembrete: Sua cirurgia de {agendamento.tipo_cirurgia} está agendada para amanhã às {agendamento.data_cirurgia.strftime("%H:%M")} no {agendamento.hospital.nome}.',
                        tipo='lembrete'
                    )
                    
                    db.session.add(notificacao)
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao enviar lembretes automáticos: {e}")
            return False
    
    @staticmethod
    def marcar_como_lida(notificacao_id, usuario_id):
        """Marca notificação como lida"""
        try:
            notificacao = Notificacao.query.filter_by(
                id=notificacao_id,
                usuario_id=usuario_id
            ).first()
            
            if notificacao:
                notificacao.lida = True
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao marcar notificação como lida: {e}")
            return False
    
    @staticmethod
    def marcar_todas_como_lidas(usuario_id):
        """Marca todas as notificações como lidas para um usuário"""
        try:
            Notificacao.query.filter_by(
                usuario_id=usuario_id,
                lida=False
            ).update({'lida': True})
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao marcar todas as notificações como lidas: {e}")
            return False
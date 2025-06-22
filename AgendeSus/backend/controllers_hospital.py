"""
Controller para Hospital - AgendeSUS DF
"""

from app_init import db
from models.hospital import Hospital
from datetime import datetime, timedelta
import json


class HospitalController:
    
    @staticmethod
    def criar_hospital(dados):
        """Cria um novo hospital"""
        try:
            hospital = Hospital(
                nome=dados['nome'],
                endereco=dados['endereco'],
                telefone=dados.get('telefone', ''),
                capacidade_cirurgica=dados.get('capacidade_cirurgica', 10),
                ativo=dados.get('ativo', True)
            )
            
            # Definir especialidades se fornecidas
            if 'especialidades' in dados:
                if isinstance(dados['especialidades'], list):
                    hospital.set_especialidades_list(dados['especialidades'])
                else:
                    hospital.especialidades = dados['especialidades']
            
            db.session.add(hospital)
            db.session.commit()
            
            return {'success': True, 'hospital_id': hospital.id, 'hospital': hospital}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def atualizar_hospital(hospital_id, dados):
        """Atualiza dados do hospital"""
        try:
            hospital = Hospital.query.get(hospital_id)
            if not hospital:
                return {'success': False, 'message': 'Hospital não encontrado'}
            
            # Atualizar campos
            for campo, valor in dados.items():
                if hasattr(hospital, campo):
                    if campo == 'especialidades' and isinstance(valor, list):
                        hospital.set_especialidades_list(valor)
                    else:
                        setattr(hospital, campo, valor)
            
            db.session.commit()
            
            return {'success': True, 'hospital': hospital}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def desativar_hospital(hospital_id):
        """Desativa um hospital"""
        try:
            hospital = Hospital.query.get(hospital_id)
            if not hospital:
                return {'success': False, 'message': 'Hospital não encontrado'}
            
            hospital.ativo = False
            db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def reativar_hospital(hospital_id):
        """Reativa um hospital"""
        try:
            hospital = Hospital.query.get(hospital_id)
            if not hospital:
                return {'success': False, 'message': 'Hospital não encontrado'}
            
            hospital.ativo = True
            db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def listar_hospitais(apenas_ativos=True):
        """Lista todos os hospitais"""
        try:
            query = Hospital.query
            
            if apenas_ativos:
                query = query.filter_by(ativo=True)
            
            hospitais = query.order_by(Hospital.nome).all()
            
            return {
                'success': True,
                'hospitais': [hospital.to_dict() for hospital in hospitais]
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def buscar_hospital(hospital_id):
        """Busca hospital específico"""
        try:
            hospital = Hospital.query.get(hospital_id)
            if not hospital:
                return {'success': False, 'message': 'Hospital não encontrado'}
            
            return {'success': True, 'hospital': hospital}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def buscar_por_especialidade(especialidade):
        """Busca hospitais que atendem determinada especialidade"""
        try:
            hospitais = Hospital.query.filter(
                Hospital.ativo == True,
                Hospital.especialidades.contains(especialidade)
            ).all()
            
            return {
                'success': True,
                'hospitais': [hospital.to_dict() for hospital in hospitais]
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def verificar_capacidade_disponivel(hospital_id, data_cirurgia):
        """Verifica capacidade disponível para determinada data"""
        try:
            hospital = Hospital.query.get(hospital_id)
            if not hospital:
                return {'success': False, 'message': 'Hospital não encontrado'}
            
            disponivel = hospital.verificar_capacidade(data_cirurgia)
            
            return {
                'success': True,
                'disponivel': disponivel,
                'capacidade_total': hospital.capacidade_cirurgica
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_ocupacao_periodo(hospital_id, data_inicio, data_fim):
        """Retorna ocupação do hospital em um período"""
        try:
            from models.agendamento import Agendamento
            
            # Buscar agendamentos no período
            agendamentos = Agendamento.query.filter(
                Agendamento.hospital_id == hospital_id,
                Agendamento.data_cirurgia.between(data_inicio, data_fim),
                Agendamento.status.in_(['agendado', 'confirmado', 'realizado'])
            ).all()
        except:
            models.agendamento = FileNotFoundError
            # Agrupar por data
            
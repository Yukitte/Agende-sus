from flask import Blueprint, request, jsonify
from models import Agendamento, Usuario, db
from datetime import datetime
from .auth import token_required

agendamentos_bp = Blueprint('agendamentos', __name__)

@agendamentos_bp.route('/api/solicitar_agendamento', methods=['POST'])
@token_required
def solicitar_agendamento(current_user):
    data = request.get_json()
    
    if not data or not data.get('especialidade') or not data.get('observacoes'):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    # Verifica se o CPF do paciente existe (se for diferente do usuário logado)
    if 'cpf_paciente' in data:
        paciente = Usuario.query.filter_by(cpf=data['cpf_paciente'], tipo_usuario='paciente').first()
        if not paciente:
            return jsonify({'message': 'Paciente não encontrado'}), 404
    else:
        paciente = current_user
    
    novo_agendamento = Agendamento(
        paciente_id=paciente.id,
        especialidade=data['especialidade'],
        data_agendamento=datetime.strptime(data.get('data_agendamento', datetime.utcnow().isoformat()), '%Y-%m-%dT%H:%M:%S'),
        status='pendente',
        descricao=data.get('descricao', ''),
        observacoes=data['observacoes']
    )
    
    db.session.add(novo_agendamento)
    db.session.commit()
    
    return jsonify({
        'message': 'Solicitação de agendamento enviada com sucesso',
        'agendamento_id': novo_agendamento.id
    }), 201

@agendamentos_bp.route('/api/meus_agendamentos/<int:user_id>', methods=['GET'])
@token_required
def meus_agendamentos(current_user, user_id):
    if current_user.id != user_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    agendamentos = Agendamento.query.filter_by(paciente_id=user_id).all()
    
    resultado = []
    for agendamento in agendamentos:
        resultado.append({
            'id': agendamento.id,
            'especialidade': agendamento.especialidade,
            'data_agendamento': agendamento.data_agendamento.isoformat(),
            'status': agendamento.status,
            'descricao': agendamento.descricao,
            'observacoes': agendamento.observacoes,
            'data_criacao': agendamento.data_criacao.isoformat()
        })
    
    return jsonify({'agendamentos': resultado})

@agendamentos_bp.route('/api/agendamentos/<int:agendamento_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def gerenciar_agendamento(current_user, agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verifica se o usuário tem permissão
    if current_user.id != agendamento.paciente_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    if request.method == 'GET':
        return jsonify({
            'id': agendamento.id,
            'paciente_id': agendamento.paciente_id,
            'especialidade': agendamento.especialidade,
            'data_agendamento': agendamento.data_agendamento.isoformat(),
            'status': agendamento.status,
            'descricao': agendamento.descricao,
            'observacoes': agendamento.observacoes
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        if 'status' in data:
            agendamento.status = data['status']
        if 'data_agendamento' in data:
            agendamento.data_agendamento = datetime.strptime(data['data_agendamento'], '%Y-%m-%dT%H:%M:%S')
        if 'observacoes' in data:
            agendamento.observacoes = data['observacoes']
        
        db.session.commit()
        return jsonify({'message': 'Agendamento atualizado com sucesso'})
    
    elif request.method == 'DELETE':
        db.session.delete(agendamento)
        db.session.commit()
        return jsonify({'message': 'Agendamento cancelado com sucesso'})
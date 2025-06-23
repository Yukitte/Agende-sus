from flask import Blueprint, request, jsonify
from models import Mensagem, Usuario, db
from datetime import datetime
from .auth import token_required

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat/<int:agendamento_id>/messages', methods=['GET'])
@token_required
def get_messages(current_user, agendamento_id):
    # Em nosso sistema, o agendamento_id 0 é a conversa com a IA Helena
    if agendamento_id == 0:
        # Busca todas as mensagens entre o usuário e a IA (usuário com ID 0)
        messages = Mensagem.query.filter(
            ((Mensagem.remetente_id == current_user.id) & (Mensagem.destinatario_id == 0)) |
            ((Mensagem.remetente_id == 0) & (Mensagem.destinatario_id == current_user.id))
        ).order_by(Mensagem.data_envio).all()
    else:
        # Para outros agendamentos, verifica se o usuário tem permissão
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        if current_user.id != agendamento.paciente_id and current_user.id != agendamento.medico_id:
            return jsonify({'message': 'Não autorizado'}), 403
        
        messages = Mensagem.query.filter(
            ((Mensagem.remetente_id == agendamento.paciente_id) & (Mensagem.destinatario_id == agendamento.medico_id)) |
            ((Mensagem.remetente_id == agendamento.medico_id) & (Mensagem.destinatario_id == agendamento.paciente_id))
        ).order_by(Mensagem.data_envio).all()
    
    resultado = []
    for msg in messages:
        resultado.append({
            'id': msg.id,
            'remetente_id': msg.remetente_id,
            'destinatario_id': msg.destinatario_id,
            'mensagem': msg.mensagem,
            'tipo_mensagem': msg.tipo_mensagem,
            'arquivo_url': msg.arquivo_url,
            'lida': msg.lida,
            'data_envio': msg.data_envio.isoformat()
        })
    
    return jsonify({'mensagens': resultado})

@chat_bp.route('/api/chat/<int:agendamento_id>/send', methods=['POST'])
@token_required
def send_message(current_user, agendamento_id):
    data = request.get_json()
    
    if not data or not data.get('mensagem'):
        return jsonify({'message': 'Mensagem é obrigatória'}), 400
    
    destinatario_id = 0  # Padrão para IA Helena
    resposta_ia = None
    
    if agendamento_id != 0:
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        
        if current_user.id == agendamento.paciente_id:
            destinatario_id = agendamento.medico_id if agendamento.medico_id else 0
        elif current_user.id == agendamento.medico_id:
            destinatario_id = agendamento.paciente_id
        else:
            return jsonify({'message': 'Não autorizado'}), 403
    
    nova_mensagem = Mensagem(
        remetente_id=current_user.id,
        destinatario_id=destinatario_id,
        mensagem=data['mensagem'],
        tipo_mensagem=data.get('tipo_mensagem', 'texto'),
        arquivo_url=data.get('arquivo_url')
    )
    
    db.session.add(nova_mensagem)
    db.session.commit()
    
    # Se estiver conversando com a IA, gera uma resposta automática
    if destinatario_id == 0:
        resposta_ia = Mensagem(
            remetente_id=0,
            destinatario_id=current_user.id,
            mensagem=f"Olá {current_user.nome.split()[0]}, sou a Helena, sua assistente virtual. Estou analisando sua mensagem: '{data['mensagem']}'. Em breve retornarei com mais informações.",
            tipo_mensagem='texto'
        )
        db.session.add(resposta_ia)
        db.session.commit()
        
        resposta_ia = {
            'id': resposta_ia.id,
            'remetente_id': resposta_ia.remetente_id,
            'destinatario_id': resposta_ia.destinatario_id,
            'mensagem': resposta_ia.mensagem,
            'tipo_mensagem': resposta_ia.tipo_mensagem,
            'data_envio': resposta_ia.data_envio.isoformat()
        }
    
    return jsonify({
        'message': 'Mensagem enviada com sucesso',
        'mensagem': {
            'id': nova_mensagem.id,
            'remetente_id': nova_mensagem.remetente_id,
            'destinatario_id': nova_mensagem.destinatario_id,
            'mensagem': nova_mensagem.mensagem,
            'tipo_mensagem': nova_mensagem.tipo_mensagem,
            'data_envio': nova_mensagem.data_envio.isoformat()
        },
        'resposta_ia': resposta_ia
    }), 201

@chat_bp.route('/api/chat/<int:agendamento_id>/mark_read/<int:user_id>', methods=['PUT'])
def mark_messages_as_read(agendamento_id, user_id):
    # Marca todas as mensagens não lidas como lidas
    Mensagem.query.filter_by(destinatario_id=user_id, lida=False).update({'lida': True})
    db.session.commit()
    
    return jsonify({'message': 'Mensagens marcadas como lidas'})
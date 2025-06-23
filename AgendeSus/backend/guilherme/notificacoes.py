from flask import Blueprint, request, jsonify
from models import Notificacao, Usuario, db
from datetime import datetime
from .auth import token_required

notificacoes_bp = Blueprint('notificacoes', __name__)

@notificacoes_bp.route('/api/notificacoes/<int:user_id>', methods=['GET'])
@token_required
def get_notifications(current_user, user_id):
    if current_user.id != user_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    notificacoes = Notificacao.query.filter_by(usuario_id=user_id).order_by(Notificacao.data_envio.desc()).all()
    
    resultado = []
    for notif in notificacoes:
        resultado.append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensagem': notif.mensagem,
            'tipo': notif.tipo,
            'prioridade': notif.prioridade,
            'lida': notif.lida,
            'data_envio': notif.data_envio.isoformat()
        })
    
    return jsonify({'notificacoes': resultado})

@notificacoes_bp.route('/api/notificacoes/marcar_lida/<int:notificacao_id>', methods=['PUT'])
@token_required
def mark_notification_as_read(current_user, notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    
    if current_user.id != notificacao.usuario_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    notificacao.lida = True
    db.session.commit()
    
    return jsonify({'message': 'Notificação marcada como lida'})

@notificacoes_bp.route('/api/notificacoes/marcar_todas_lidas/<int:user_id>', methods=['POST'])
@token_required
def mark_all_notifications_as_read(current_user, user_id):
    if current_user.id != user_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    Notificacao.query.filter_by(usuario_id=user_id, lida=False).update({'lida': True})
    db.session.commit()
    
    return jsonify({'message': 'Todas as notificações foram marcadas como lidas'})

def criar_notificacao(usuario_id, titulo, mensagem, tipo='informacao', prioridade='normal'):
    nova_notificacao = Notificacao(
        usuario_id=usuario_id,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        prioridade=prioridade
    )
    
    db.session.add(nova_notificacao)
    db.session.commit()
    
    return nova_notificacao
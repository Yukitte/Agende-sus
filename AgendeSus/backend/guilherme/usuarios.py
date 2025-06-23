from flask import Blueprint, request, jsonify
from models import Usuario, db
from werkzeug.security import generate_password_hash
from datetime import datetime
from .auth import token_required

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/api/meus_dados/<int:user_id>', methods=['GET'])
@token_required
def meus_dados(current_user, user_id):
    if current_user.id != user_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    usuario = Usuario.query.get_or_404(user_id)
    
    return jsonify({
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email,
        'cpf': usuario.cpf,
        'telefone': usuario.telefone,
        'data_nascimento': usuario.data_nascimento.isoformat(),
        'genero': usuario.genero,
        'endereco': usuario.endereco,
        'cartao_sus': usuario.cartao_sus,
        'tipo_usuario': usuario.tipo_usuario,
        'receber_emails': usuario.receber_emails,
        'receber_sms': usuario.receber_sms
    })

@usuarios_bp.route('/api/atualizar_meus_dados/<int:user_id>', methods=['PUT'])
@token_required
def atualizar_meus_dados(current_user, user_id):
    if current_user.id != user_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    usuario = Usuario.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'nome' in data:
        usuario.nome = data['nome']
    if 'telefone' in data:
        usuario.telefone = data['telefone']
    if 'data_nascimento' in data:
        usuario.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
    if 'genero' in data:
        usuario.genero = data['genero']
    if 'endereco' in data:
        usuario.endereco = data['endereco']
    if 'receber_emails' in data:
        usuario.receber_emails = data['receber_emails']
    if 'receber_sms' in data:
        usuario.receber_sms = data['receber_sms']
    
    db.session.commit()
    
    return jsonify({'message': 'Dados atualizados com sucesso'})

@usuarios_bp.route('/api/alterar_senha/<int:user_id>', methods=['PUT'])
@token_required
def alterar_senha(current_user, user_id):
    if current_user.id != user_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    usuario = Usuario.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data or not data.get('senha_atual') or not data.get('nova_senha'):
        return jsonify({'message': 'Senha atual e nova senha são obrigatórias'}), 400
    
    if not check_password_hash(usuario.senha, data['senha_atual']):
        return jsonify({'message': 'Senha atual incorreta'}), 401
    
    usuario.senha = generate_password_hash(data['nova_senha'])
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'})

@usuarios_bp.route('/api/configuracoes/<int:user_id>', methods=['GET'])
@token_required
def get_configuracoes(current_user, user_id):
    if current_user.id != user_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    usuario = Usuario.query.get_or_404(user_id)
    
    return jsonify({
        'receber_emails': usuario.receber_emails,
        'receber_sms': usuario.receber_sms
    })

@usuarios_bp.route('/api/atualizar_configuracoes/<int:user_id>', methods=['PUT'])
@token_required
def atualizar_configuracoes(current_user, user_id):
    if current_user.id != user_id and current_user.tipo_usuario != 'admin':
        return jsonify({'message': 'Não autorizado'}), 403
    
    usuario = Usuario.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'receber_emails' in data:
        usuario.receber_emails = data['receber_emails']
    if 'receber_sms' in data:
        usuario.receber_sms = data['receber_sms']
    
    db.session.commit()
    
    return jsonify({'message': 'Configurações atualizadas com sucesso'})
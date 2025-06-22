# utils_decorators.py
# AgendeSUS DF - Decoradores para controle de acesso e autenticação

from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from models_usuarios import Usuario

def login_required(f):
    """
    Decorador que exige que o usuário esteja logado para acessar a rota.
    Redireciona para login se não estiver autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('routes_usuario.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorador que exige que o usuário seja administrador.
    Verifica se está logado E se é admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('routes_usuario.login'))
        
        user = Usuario.query.get(session['user_id'])
        if not user or user.tipo_usuario != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
            return redirect(url_for('routes_dashboard.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def medico_required(f):
    """
    Decorador que exige que o usuário seja médico ou admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('routes_usuario.login'))
        
        user = Usuario.query.get(session['user_id'])
        if not user or user.tipo_usuario not in ['medico', 'admin']:
            flash('Acesso negado. Apenas médicos podem acessar esta página.', 'danger')
            return redirect(url_for('routes_dashboard.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def paciente_required(f):
    """
    Decorador que exige que o usuário seja paciente.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('routes_usuario.login'))
        
        user = Usuario.query.get(session['user_id'])
        if not user or user.tipo_usuario != 'paciente':
            flash('Acesso negado. Apenas pacientes podem acessar esta página.', 'warning')
            return redirect(url_for('routes_dashboard.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def api_login_required(f):
    """
    Decorador para APIs que retorna JSON em vez de redirect.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False, 
                'message': 'Autenticação necessária',
                'error_code': 'AUTH_REQUIRED'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def api_admin_required(f):
    """
    Decorador para APIs administrativas que retorna JSON.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Autenticação necessária',
                'error_code': 'AUTH_REQUIRED'
            }), 401
        
        user = Usuario.query.get(session['user_id'])
        if not user or user.tipo_usuario != 'admin':
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Privilégios de administrador necessários.',
                'error_code': 'ADMIN_REQUIRED'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def validate_ownership(model_class, id_param='id', user_field='usuario_id'):
    """
    Decorador que valida se o usuário é dono do recurso.
    Útil para garantir que pacientes só vejam seus próprios dados.
    
    Args:
        model_class: Classe do modelo (ex: Agendamento)
        id_param: Nome do parâmetro que contém o ID (ex: 'agendamento_id')
        user_field: Campo que relaciona com o usuário (ex: 'paciente.usuario_id')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Você precisa fazer login para acessar esta página.', 'warning')
                return redirect(url_for('routes_usuario.login'))
            
            # Pegar o ID do recurso
            resource_id = kwargs.get(id_param) or request.args.get(id_param)
            if not resource_id:
                flash('Recurso não encontrado.', 'danger')
                return redirect(url_for('routes_dashboard.dashboard'))
            
            # Buscar o recurso
            resource = model_class.query.get(resource_id)
            if not resource:
                flash('Recurso não encontrado.', 'danger')
                return redirect(url_for('routes_dashboard.dashboard'))
            
            # Verificar ownership
            user = Usuario.query.get(session['user_id'])
            
            # Admin pode acessar tudo
            if user.tipo_usuario == 'admin':
                return f(*args, **kwargs)
            
            # Verificar se é o dono do recurso
            if hasattr(resource, user_field):
                resource_user_id = getattr(resource, user_field)
            else:
                # Para relacionamentos mais complexos (ex: agendamento.paciente.usuario_id)
                parts = user_field.split('.')
                resource_user_id = resource
                for part in parts:
                    resource_user_id = getattr(resource_user_id, part)
            
            if resource_user_id != user.id:
                flash('Você não tem permissão para acessar este recurso.', 'danger')
                return redirect(url_for('routes_dashboard.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_user_active(f):
    """
    Decorador que verifica se o usuário está ativo.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            user = Usuario.query.get(session['user_id'])
            if not user or not user.ativo:
                session.clear()
                flash('Sua conta foi desativada. Entre em contato com o suporte.', 'danger')
                return redirect(url_for('routes_usuario.login'))
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=60, window=60):
    """
    Decorador simples para rate limiting.
    
    Args:
        max_requests: Número máximo de requests
        window: Janela de tempo em segundos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Implementação básica usando session
            # Em produção, usar Redis ou similar
            
            from datetime import datetime, timedelta
            
            key = f"rate_limit_{request.remote_addr}_{f.__name__}"
            now = datetime.now()
            
            if key not in session:
                session[key] = {'count': 1, 'reset_time': now + timedelta(seconds=window)}
            else:
                rate_data = session[key]
                
                # Resetar contador se passou da janela
                if now > rate_data['reset_time']:
                    session[key] = {'count': 1, 'reset_time': now + timedelta(seconds=window)}
                else:
                    # Incrementar contador
                    rate_data['count'] += 1
                    session[key] = rate_data
                    
                    # Verificar limite
                    if rate_data['count'] > max_requests:
                        return jsonify({
                            'success': False,
                            'message': 'Muitas requisições. Tente novamente em alguns minutos.',
                            'error_code': 'RATE_LIMIT_EXCEEDED'
                        }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_action(action_type, description=None):
    """
    Decorador para registrar ações do usuário (auditoria).
    
    Args:
        action_type: Tipo da ação (ex: 'CREATE_APPOINTMENT', 'CANCEL_APPOINTMENT')
        description: Descrição adicional
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Executar a função
            result = f(*args, **kwargs)
            
            # Registrar a ação (implementar conforme necessário)
            if 'user_id' in session:
                try:
                    from datetime import datetime
                    # Aqui você pode implementar log em banco de dados
                    # ou arquivo de log conforme necessário
                    
                    log_entry = {
                        'user_id': session['user_id'],
                        'action_type': action_type,
                        'description': description or f"Executed {f.__name__}",
                        'timestamp': datetime.now(),
                        'ip_address': request.remote_addr,
                        'user_agent': request.user_agent.string
                    }
                    
                    # Exemplo: salvar em arquivo de log
                    import json
                    with open('logs/user_actions.log', 'a') as log_file:
                        log_file.write(json.dumps(log_entry, default=str) + '\n')
                        
                except Exception as e:
                    # Não falhar a operação por causa do log
                    print(f"Erro ao registrar ação: {e}")
            
            return result
        return decorated_function
    return decorator

# Função auxiliar para obter usuário atual
def get_current_user():
    """
    Função auxiliar para obter o usuário atual da sessão.
    Retorna None se não estiver logado.
    """
    if 'user_id' not in session:
        return None
    
    try:
        return Usuario.query.get(session['user_id'])
    except:
        return None

# Função auxiliar para verificar permissões
def has_permission(user, permission):
    """
    Verifica se o usuário tem uma permissão específica.
    
    Args:
        user: Objeto Usuario
        permission: String da permissão (ex: 'view_all_appointments')
    """
    if not user:
        return False
    
    # Admin tem todas as permissões
    if user.tipo_usuario == 'admin':
        return True
    
    # Mapeamento de permissões por tipo de usuário
    permissions_map = {
        'paciente': [
            'view_own_appointments',
            'create_appointment',
            'cancel_own_appointment',
            'view_own_notifications',
            'use_chat'
        ],
        'medico': [
            'view_assigned_appointments',
            'update_appointment_status',
            'view_patient_history',
            'use_chat',
            'view_hospital_schedule'
        ],
        'admin': ['*']  # Todas as permissões
    }
    
    user_permissions = permissions_map.get(user.tipo_usuario, [])
    return permission in user_permissions or '*' in user_permissions
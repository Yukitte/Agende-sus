from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, date

# Importa os modelos do seu arquivo models.py
from models import db, Usuario, Medico, Especialidade, Horario, Consulta

# Inicialização do Flask com configuração para arquivos estáticos:
# static_folder: Define o caminho RELATIVO da pasta 'static' a partir do diretório onde app.py está.
#                '../static' significa um nível acima, na pasta 'SeuProjetoRaiz/static'.
# static_url_path: Define o prefixo da URL para acessar esses arquivos.
#                  '/' significa que um arquivo como 'home.html' em 'static/' será acessível em '/home.html'.
app = Flask(__name__, static_folder='../static', static_url_path='/')

# Configurações do aplicativo
# SQLALCHEMY_DATABASE_URI: Caminho para o seu banco de dados SQLite dentro da pasta 'instance'.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/database.db'
app.config['JWT_SECRET_KEY'] = 'secreta123'

# Inicialização das extensões Flask
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

# --- ROTAS PARA SERVIR ARQUIVOS HTML ESTÁTICOS ---
# Cada rota aponta para um arquivo HTML específico dentro da pasta estática.
# O send_from_directory() é a função correta para isso.

@app.route('/')
def index():
    # Serve a página 'home.html' quando o usuário acessa a URL base (ex: http://127.0.0.1:5501/)
    return send_from_directory(app.static_folder, 'home.html')

@app.route('/home.html')
def home_page():
    # Serve a página 'home.html' quando acessada diretamente (ex: http://127.0.0.1:5501/home.html)
    return send_from_directory(app.static_folder, 'home.html')

@app.route('/login.html')
def login_page():
    # Serve a página 'login.html'
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/cadastro.html')
def cadastro_page():
    # Serve a página 'cadastro.html'. Esta é a rota que precisamos verificar!
    return send_from_directory(app.static_folder, 'cadastro.html')

@app.route('/meus_dados.html')
def meus_dados_page():
    return send_from_directory(app.static_folder, 'meus_dados.html')

@app.route('/agendamento.html')
def agendamento_page():
    return send_from_directory(app.static_folder, 'agendamento.html')

@app.route('/configuracoes.html')
def configuracoes_page():
    return send_from_directory(app.static_folder, 'configuracoes.html')

# Rota para servir arquivos dentro da subpasta 'imagens' de 'static'.
# A URL será '/imagens/<nome_do_arquivo>', ex: http://127.0.0.1:5501/imagens/logo.png
@app.route('/imagens/<path:filename>')
def serve_image(filename):
    return send_from_directory(f"{app.static_folder}/imagens", filename)

# --- SUAS ROTAS DE API (BACKEND) ---
# Essas rotas não servem arquivos, mas lidam com a lógica de negócio e banco de dados.

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    
    nome = data.get('nome')
    email = data.get('email')
    cpf = data.get('cpf')
    telefone = data.get('telefone')
    data_nascimento_str = data.get('data_nascimento')
    genero = data.get('genero')
    endereco_completo = data.get('endereco_completo')
    senha = data.get('senha')
    cartao_sus = data.get('cartao_sus')
    tipo = data.get('tipo', 'paciente')

    if not all([nome, email, cpf, telefone, data_nascimento_str, genero, endereco_completo, senha, cartao_sus]):
        return jsonify({'message': 'Todos os campos são obrigatórios'}), 400

    if len(senha) < 6:
        return jsonify({'message': 'A senha deve ter pelo menos 6 caracteres.'}), 400
    if not cpf.isdigit() or len(cpf) != 11:
        return jsonify({'message': 'CPF inválido. Deve conter 11 dígitos numéricos.'}), 400
    if not telefone.isdigit() or not (10 <= len(telefone) <= 11):
        return jsonify({'message': 'Telefone inválido. Deve conter 10 ou 11 dígitos numéricos.'}), 400
    if not cartao_sus.isdigit() or len(cartao_sus) != 15:
        return jsonify({'message': 'Número do Cartão SUS inválido. Deve conter 15 dígitos numéricos.'}), 400

    try:
        data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Formato de data de nascimento inválido. Use AAAA-MM-DD.'}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'message': 'Email já cadastrado.'}), 409
    if Usuario.query.filter_by(cpf=cpf).first():
        return jsonify({'message': 'CPF já cadastrado.'}), 409
    if Usuario.query.filter_by(cartao_sus=cartao_sus).first():
        return jsonify({'message': 'Número do Cartão SUS já cadastrado.'}), 409

    try:
        hashed_password = bcrypt.generate_password_hash(senha).decode('utf-8')
        
        new_user = Usuario(
            nome=nome,
            email=email,
            senha_hash=hashed_password,
            cpf=cpf,
            telefone=telefone,
            data_nascimento=data_nascimento,
            genero=genero,
            endereco_completo=endereco_completo,
            cartao_sus=cartao_sus,
            tipo=tipo
        )
        
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuário registrado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar usuário: {e}")
        return jsonify({'message': 'Erro interno do servidor ao registrar usuário.'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = Usuario.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.senha_hash, data['senha']):
        token = create_access_token(identity=user.id)
        return jsonify({'token': token, 'nome': user.nome, 'tipo': user.tipo}), 200
    return jsonify({'message': 'Credenciais inválidas'}), 401

@app.route('/especialidades', methods=['GET', 'POST'])
@jwt_required()
def especialidades():
    if request.method == 'POST':
        data = request.json
        if 'nome' not in data:
            return jsonify({'message': 'Nome da especialidade é obrigatório.'}), 400
        esp = Especialidade(nome=data['nome'])
        db.session.add(esp)
        db.session.commit()
        return jsonify({'message': 'Especialidade cadastrada'}), 201
    all_esp = Especialidade.query.all()
    return jsonify([{'id': e.id, 'nome': e.nome} for e in all_esp])

@app.route('/medicos', methods=['GET', 'POST'])
@jwt_required()
def medicos():
    if request.method == 'POST':
        data = request.json
        if 'nome' not in data or 'especialidade_id' not in data:
            return jsonify({'message': 'Nome e ID da especialidade são obrigatórios.'}), 400
        
        especialidade = Especialidade.query.get(data['especialidade_id'])
        if not especialidade:
            return jsonify({'message': 'Especialidade não encontrada.'}), 404

        m = Medico(nome=data['nome'], especialidade_id=data['especialidade_id'])
        db.session.add(m)
        db.session.commit()
        return jsonify({'message': 'Médico cadastrado'}), 201
    all_med = Medico.query.all()
    return jsonify([{'id': m.id, 'nome': m.nome, 'especialidade': m.especialidade.nome if m.especialidade else None} for m in all_med])

@app.route('/horarios', methods=['GET', 'POST'])
@jwt_required()
def horarios():
    if request.method == 'POST':
        data = request.json
        if not all(k in data for k in ['medico_id', 'data', 'hora']):
            return jsonify({'message': 'Médico, data e hora são obrigatórios.'}), 400
        
        try:
            data_obj = datetime.strptime(data['data'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Formato de data ou hora inválido. Use AAAA-MM-DD e HH:MM.'}), 400

        medico = Medico.query.get(data['medico_id'])
        if not medico:
            return jsonify({'message': 'Médico não encontrado.'}), 404

        h = Horario(medico_id=data['medico_id'], data=data_obj, hora=data['hora'])
        db.session.add(h)
        db.session.commit()
        return jsonify({'message': 'Horário cadastrado'}), 201
    all_hor = Horario.query.filter_by(disponivel=True).all()
    return jsonify([{'id': h.id, 'medico_id': h.medico_id, 'data': h.data.strftime('%Y-%m-%d'), 'hora': h.hora} for h in all_hor])


@app.route('/consultas', methods=['GET', 'POST'])
@jwt_required()
def consultas():
    user_id = get_jwt_identity()
    if request.method == 'POST':
        data = request.json
        if 'medico_id' not in data or 'horario_id' not in data:
            return jsonify({'message': 'Médico e horário são obrigatórios.'}), 400

        horario = Horario.query.get(data['horario_id'])
        if not horario:
            return jsonify({'message': 'Horário não encontrado.'}), 404
        if not horario.disponivel:
            return jsonify({'message': 'Horário não disponível.'}), 409

        cons = Consulta(usuario_id=user_id, medico_id=data['medico_id'], horario_id=data['horario_id'])
        horario.disponivel = False
        db.session.add(cons)
        db.session.commit()
        return jsonify({'message': 'Consulta agendada'}), 201
    
    all_cons = Consulta.query.filter_by(usuario_id=user_id).all()
    return jsonify([{'id': c.id, 'medico_id': c.medico_id, 'horario_id': c.horario_id, 'status': c.status} for c in all_cons])

@app.route('/api/meus_dados', methods=['GET'])
@jwt_required()
def meus_dados():
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.get(current_user_id)

    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'}), 404

    return jsonify({
        'nome': usuario.nome,
        'email': usuario.email,
        'cpf': usuario.cpf,
        'telefone': usuario.telefone,
        'data_nascimento': usuario.data_nascimento.strftime('%Y-%m-%d') if usuario.data_nascimento else None,
        'genero': usuario.genero,
        'endereco_completo': usuario.endereco_completo,
        'cartao_sus': usuario.cartao_sus
    }), 200

@app.route('/api/atualizar_meus_dados', methods=['PUT'])
@jwt_required()
def atualizar_meus_dados():
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.get(current_user_id)

    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'}), 404

    data = request.json

    if not all(k in data for k in ['nome', 'telefone', 'data_nascimento', 'genero', 'endereco_completo']):
        return jsonify({'message': 'Todos os campos obrigatórios (nome, telefone, data de nascimento, gênero, endereço completo) devem ser fornecidos.'}), 400

    try:
        usuario.nome = data['nome']
        usuario.telefone = data['telefone']
        usuario.genero = data['genero']
        usuario.endereco_completo = data['endereco_completo']
        
        usuario.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()

        db.session.commit()
        return jsonify({'message': 'Dados atualizados com sucesso!'}), 200
    except ValueError:
        db.session.rollback()
        return jsonify({'message': 'Formato de data de nascimento inválido. Use AAAA-MM-DD.'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar dados do usuário: {e}")
        return jsonify({'message': 'Erro interno do servidor ao atualizar dados.'}), 500

@app.route('/usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios():
    usuarios = Usuario.query.all()
    lista = []
    for u in usuarios:
        lista.append({
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'cpf': u.cpf,
            'telefone': u.telefone,
            'data_nascimento': u.data_nascimento.strftime('%Y-%m-%d'),
            'genero': u.genero,
            'endereco_completo': u.endereco_completo,
            'cartao_sus': u.cartao_sus,
            'tipo': u.tipo
        })
    return jsonify(lista)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # O aplicativo irá rodar na porta 5501.
    app.run(debug=True, port=5500, host='0.0.0.0')


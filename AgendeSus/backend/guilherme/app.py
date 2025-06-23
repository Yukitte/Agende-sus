from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

# Configuração básica do Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configuração do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Registrar blueprints (rotas)
from routes.auth import auth_bp
from routes.agendamentos import agendamentos_bp
from routes.chat import chat_bp
from routes.notificacoes import notificacoes_bp
from routes.usuarios import usuarios_bp

app.register_blueprint(auth_bp)
app.register_blueprint(agendamentos_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(notificacoes_bp)
app.register_blueprint(usuarios_bp)

# Rota de teste
@app.route('/')
def index():
    return jsonify({"message": "Bem-vindo ao AgendeSUS API"})

if __name__ == '__main__':
    app.run(debug=True)
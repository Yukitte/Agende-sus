"""
AgendeSUS DF - Sistema de Agendamento de Cirurgias
Factory da aplicação Flask
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# Instâncias das extensões
db = SQLAlchemy()
mail = Mail()

def create_app(config_name='development'):
    """
    Factory para criar a aplicação Flask
    
    Args:
        config_name (str): Nome da configuração ('development', 'testing', 'production')
    
    Returns:
        Flask: Instância da aplicação configurada
    """
    app = Flask(__name__)
    
    # Configurações
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    mail.init_app(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar manipuladores de erro
    register_error_handlers(app)
    
    # Registrar comandos CLI
    register_cli_commands(app)
    
    return app

def register_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    
    # Blueprint principal
    from app.views.main import main_bp
    app.register_blueprint(main_bp)
    
    # Blueprint de autenticação
    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Blueprint de agendamentos
    from app.views.agendamento import agendamento_bp
    app.register_blueprint(agendamento_bp, url_prefix='/agendamento')
    
    # Blueprint administrativo
    from app.views.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Blueprint de API
    from app.views.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

def register_error_handlers(app):
    """Registra manipuladores de erro customizados"""
    
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

def register_cli_commands(app):
    """Registra comandos CLI customizados"""
    
    @app.cli.command()
    def init_db():
        """Inicializa o banco de dados"""
        from app.services.database_service import init_database
        init_database()
        print("Banco de dados inicializado com sucesso!")
    
    @app.cli.command()
    def create_tables():
        """Cria todas as tabelas do banco"""
        db.create_all()
        print("Tabelas criadas com sucesso!")
    
    @app.cli.command()
    def drop_tables():
        """Remove todas as tabelas do banco"""
        db.drop_all()
        print("Tabelas removidas com sucesso!")
    
    @app.cli.command()
    def seed_data():
        """Popula o banco com dados de exemplo"""
        from app.services.database_service import criar_dados_iniciais
        criar_dados_iniciais()
        print("Dados de exemplo criados com sucesso!")
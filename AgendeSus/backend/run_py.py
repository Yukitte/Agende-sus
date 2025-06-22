#!/usr/bin/env python3
"""
AgendeSUS DF - Sistema de Agendamento de Cirurgias
Arquivo principal de execução da aplicação
"""

import os
import sys
from app import create_app
from app.services.database_service import init_database

def main():
    """Função principal de execução"""
    # Criar aplicação
    app = create_app()
    
    # Verificar argumentos de linha de comando
    if '--test' in sys.argv:
        # Executar testes
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover('tests')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    
    elif '--init-db' in sys.argv:
        # Inicializar banco de dados
        with app.app_context():
            init_database()
        print("Banco de dados inicializado com sucesso!")
        return
    
    # Executar aplicação em modo desenvolvimento
    print("=" * 50)
    print("AgendeSUS DF - Sistema de Agendamento de Cirurgias")
    print("=" * 50)
    print("Acesse: http://localhost:5000")
    print("\nContas de teste disponíveis:")
    print("• Admin: admin@saude.df.gov.br / admin123")
    print("• Médico: medico@saude.df.gov.br / medico123") 
    print("• Paciente: paciente@teste.com / paciente123")
    print("=" * 50)
    
    # Configurações de desenvolvimento
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    app.run(
        debug=debug_mode,
        host=host,
        port=port,
        threaded=True
    )

if __name__ == '__main__':
    main()
from app import app, db, Usuario, Medico, Especialidade, Horario, Consulta # Importe o que precisar verificar

def check_users():
    with app.app_context():
        print("--- Verificando Tabela de Usuários ---")
        users = Usuario.query.all()
        if not users:
            print("Nenhum usuário encontrado.")
            return

        for user in users:
            print(f"ID: {user.id}")
            print(f"  Nome: {user.nome}")
            print(f"  Email: {user.email}")
            print(f"  CPF: {user.cpf}")
            print(f"  Telefone: {user.telefone}")
            print(f"  Data Nasc: {user.data_nascimento}")
            print(f"  Gênero: {user.genero}")
            print(f"  Endereço: {user.endereco_completo}")
            print(f"  Cartão SUS: {user.cartao_sus}")
            print(f"  Tipo: {user.tipo}")
            print(f"  Senha Hash: {user.senha_hash[:10]}...") # Mostra apenas o início do hash
            print("-" * 30)

# Você pode adicionar funções semelhantes para outras tabelas:
def check_medicos():
    with app.app_context():
        print("\n--- Verificando Tabela de Médicos ---")
        medicos = Medico.query.all()
        if not medicos:
            print("Nenhum médico encontrado.")
            return
        for medico in medicos:
            especialidade_nome = medico.especialidade.nome if medico.especialidade else "N/A"
            print(f"ID: {medico.id}, Nome: {medico.nome}, Especialidade: {especialidade_nome}")

if __name__ == '__main__':
    check_users()
    check_medicos() # Chame outras funções de verificação aqui
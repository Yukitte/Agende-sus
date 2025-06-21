import pandas as pd
from datetime import datetime

# DataFrames simulando banco de dados
pacientes_df = pd.DataFrame(columns=['id', 'nome', 'cpf'])
medicos_df = pd.DataFrame(columns=['id', 'nome', 'especialidade'])
cirurgias_df = pd.DataFrame(columns=['id', 'data', 'paciente_id', 'medico_id', 'status'])

# Geradores de ID automático
def gerar_id(df):
    return len(df) + 1

# Cadastro de paciente
def cadastrar_paciente(nome, cpf):
    global pacientes_df
    novo_id = gerar_id(pacientes_df)
    novo_paciente = pd.DataFrame([{'id': novo_id, 'nome': nome, 'cpf': cpf}])
    pacientes_df = pd.concat([pacientes_df, novo_paciente], ignore_index=True)
    print(f"Paciente {nome} cadastrado com ID {novo_id}")

# Cadastro de médico
def cadastrar_medico(nome, especialidade):
    global medicos_df
    novo_id = gerar_id(medicos_df)
    novo_medico = pd.DataFrame([{'id': novo_id, 'nome': nome, 'especialidade': especialidade}])
    medicos_df = pd.concat([medicos_df, novo_medico], ignore_index=True)
    print(f"Médico {nome} cadastrado com ID {novo_id}")

# Agendamento de cirurgia
def agendar_cirurgia(paciente_id, medico_id, data_str):
    global cirurgias_df
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d %H:%M")
        novo_id = gerar_id(cirurgias_df)
        nova_cirurgia = pd.DataFrame([{
            'id': novo_id,
            'data': data,
            'paciente_id': paciente_id,
            'medico_id': medico_id,
            'status': 'agendada'
        }])
        cirurgias_df = pd.concat([cirurgias_df, nova_cirurgia], ignore_index=True)
        print(f"Cirurgia agendada para o paciente {paciente_id} com médico {medico_id} em {data}")
    except ValueError:
        print("Data inválida. Use o formato: YYYY-MM-DD HH:MM")

# Exibição dos dados
def mostrar_agendamentos():
    print("\n== CIRURGIAS AGENDADAS ==")
    print(cirurgias_df)

# Exemplo de uso
if __name__ == "_main_":
    cadastrar_paciente("Maria da Silva", "12345678900")
    cadastrar_medico("Dr. João", "Ortopedia")
    agendar_cirurgia(1, 1, "2025-07-10 08:00")
    mostrar_agendamentos()
    print(medicos_df)
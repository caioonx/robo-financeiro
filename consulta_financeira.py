import os
import mysql.connector
from getpass import getpass

# Configuracoes do banco de dados
HOST = os.getenv("DB_HOST", "localhost")
PORT = int(os.getenv("DB_PORT", "3306"))
USER = os.getenv("DB_USER", "root")
DATABASE = os.getenv("DB_NAME", "empresa_automacao")

try:
    conexao = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=getpass("Digite a senha do MySQL: "),
        database=DATABASE
    )

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT descricao, valor, vencimento, status
        FROM contas_pagar
        ORDER BY vencimento ASC
    """)

    contas = cursor.fetchall()

    print("\n===== CONTAS A PAGAR =====\n")
    print(f"Banco de dados: {DATABASE}")
    print(f"Total de registros: {len(contas)}")
    print("=" * 40)

    for conta in contas:
        print(f"Descricao: {conta[0]}")
        print(f"Valor: R$ {conta[1]:.2f}")
        print(f"Vencimento: {conta[2]}")
        print(f"Status: {conta[3]}")
        print("-" * 40)

    cursor.close()
    conexao.close()

    print("\nConsulta finalizada com sucesso!")

except mysql.connector.Error as erro:
    print(f"Erro na consulta: {erro}")
    raise SystemExit(1)
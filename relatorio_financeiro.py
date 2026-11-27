
import os
import mysql.connector
from getpass import getpass

# Configuracoes do banco de dados
HOST = os.getenv("DB_HOST", "localhost")
PORT = int(os.getenv("DB_PORT", "3306"))
USER = os.getenv("DB_USER", "root")
DATABASE = os.getenv("DB_NAME", "empresa_automacao_demo")

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
        SELECT
            COUNT(*) AS total_contas,
            COALESCE(SUM(valor), 0) AS total_despesas,
            COALESCE(SUM(CASE WHEN status = 'VENCIDO'
                THEN valor ELSE 0 END), 0) AS total_vencido,
            COALESCE(SUM(CASE WHEN status = 'PENDENTE'
                THEN valor ELSE 0 END), 0) AS total_pendente,
            COALESCE(SUM(CASE WHEN status = 'PAGO'
                THEN valor ELSE 0 END), 0) AS total_pago
        FROM contas_pagar
    """)

    resultado = cursor.fetchone()

    total_contas = resultado[0]
    total_despesas = resultado[1]
    total_vencido = resultado[2]
    total_pendente = resultado[3]
    total_pago = resultado[4]

    total_aberto = total_vencido + total_pendente

    percentual_atraso = (
        total_vencido / total_despesas * 100
        if total_despesas > 0 else 0
    )

    print("\n===== RELATORIO FINANCEIRO =====\n")
    print(f"Banco de dados: {DATABASE}")
    print("=" * 45)
    print(f"Total de contas: {total_contas}")
    print(f"Total de despesas: R$ {total_despesas:.2f}")
    print(f"Total vencido: R$ {total_vencido:.2f}")
    print(f"Total pendente: R$ {total_pendente:.2f}")
    print(f"Total pago: R$ {total_pago:.2f}")
    print(f"Total em aberto: R$ {total_aberto:.2f}")
    print(f"Percentual em atraso: {percentual_atraso:.2f}%")
    print("=" * 45)

    cursor.close()
    conexao.close()

    print("\nRelatorio gerado com sucesso!")

except mysql.connector.Error as erro:
    print(f"Erro ao gerar relatorio: {erro}")
    raise SystemExit(1)

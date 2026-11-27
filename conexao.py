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

    if conexao.is_connected():
        print("\nConexao com MySQL realizada com sucesso!")
        print(f"Banco de dados: {DATABASE}")
        conexao.close()

except mysql.connector.Error as erro:
    print(f"Erro na conexao: {erro}")
    raise SystemExit(1)
    
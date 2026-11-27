import os
import shutil
from pathlib import Path
from datetime import datetime

# Configuracao do ambiente
DATABASE = os.getenv("DB_NAME", "empresa_automacao_demo")

MODO_DEMO = DATABASE == "empresa_automacao_demo"

try:
    # Diretorio principal do projeto
    pasta = Path(__file__).resolve().parent

    # Separacao dos ambientes
    if MODO_DEMO:

        ambiente = "DEMONSTRACAO"

        arquivo = pasta / "relatorio_financeiro_demo.xlsx"

        pasta_backups = pasta / "backups" / "demo"

    elif DATABASE == "empresa_automacao":

        ambiente = "OPERACIONAL"

        arquivo = pasta / "relatorio_financeiro.xlsx"

        pasta_backups = pasta / "backups"

    else:
        raise ValueError("Banco de dados nao reconhecido.")

    # Criacao automatica da pasta
    pasta_backups.mkdir(
        parents=True,
        exist_ok=True
    )

    # Verificacao do relatorio
    if not arquivo.is_file():

        raise FileNotFoundError(
            f"Relatorio nao encontrado: {arquivo.name}"
        )

    # Data e horario do backup
    data_hora = datetime.now().strftime(
        "%Y-%m-%d_%H%M%S_%f"
    )

    # Nome do backup
    prefixo = (
        "relatorio_demo"
        if MODO_DEMO
        else "relatorio"
    )

    nome_backup = f"{prefixo}_{data_hora}.xlsx"

    destino = pasta_backups / nome_backup

    # Copia do relatorio
    shutil.copy2(arquivo, destino)

    # Tamanho do arquivo
    tamanho_kb = destino.stat().st_size / 1024

    # Resultado da operacao
    print("\n===== BACKUP FINANCEIRO =====\n")

    print(f"Banco de dados: {DATABASE}")
    print(f"Ambiente: {ambiente}")
    print(f"Arquivo original: {arquivo.name}")
    print(f"Backup: {nome_backup}")
    print(f"Tamanho: {tamanho_kb:.2f} KB")
    print(f"Local: {destino}")

    print("\nBackup realizado com sucesso!")
    print("=" * 45)

except Exception as erro:

    print(f"Erro ao realizar backup: {erro}")

    raise SystemExit(1)
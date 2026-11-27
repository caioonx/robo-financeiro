import os
import re
from pathlib import Path
from datetime import datetime, timedelta

# Configuracoes
DIAS_RETENCAO = 30
MODO_SIMULACAO = True

# Configuracao do ambiente
DATABASE = os.getenv(
    "DB_NAME",
    "empresa_automacao_demo"
)

MODO_DEMO = DATABASE == "empresa_automacao_demo"

try:

    # Diretorio principal
    pasta = Path(__file__).resolve().parent

    # Separacao dos ambientes
    if MODO_DEMO:

        ambiente = "DEMONSTRACAO"
        pasta_backups = pasta / "backups" / "demo"
        prefixo = "relatorio_demo_"

    elif DATABASE == "empresa_automacao":

        ambiente = "OPERACIONAL"
        pasta_backups = pasta / "backups"
        prefixo = "relatorio_"

    else:

        raise ValueError(
            "Banco de dados nao reconhecido."
        )

    # Criacao da pasta
    pasta_backups.mkdir(
        parents=True,
        exist_ok=True
    )

    # Data limite de retencao
    data_limite = datetime.now() - timedelta(
        days=DIAS_RETENCAO
    )

    # Contadores
    total_analisados = 0
    total_antigos = 0
    total_excluidos = 0
    total_preservados = 0
    total_ignorados = 0

    print("\n===== LIMPEZA DE BACKUPS =====\n")

    print(f"Banco de dados: {DATABASE}")
    print(f"Ambiente: {ambiente}")
    print(f"Retencao: {DIAS_RETENCAO} dias")
    print(f"Modo simulacao: {MODO_SIMULACAO}")
    print(f"Diretorio: {pasta_backups}")
    print("=" * 45)

    # Padrao de nomes permitidos
    padrao = (
        re.escape(prefixo)
        + r"\d{4}-\d{2}-\d{2}_\d{6}_\d{6}\.xlsx"
    )

    # Analise dos arquivos
    for arquivo in sorted(pasta_backups.iterdir()):

        # Protecao contra arquivos indevidos
        if arquivo.is_symlink() or not arquivo.is_file():

            total_ignorados += 1
            continue

        if not re.fullmatch(padrao, arquivo.name):

            total_ignorados += 1
            continue

        # Extracao da data do backup
        try:

            data_backup = datetime.strptime(
                arquivo.stem.removeprefix(prefixo),
                "%Y-%m-%d_%H%M%S_%f"
            )

        except ValueError:

            total_ignorados += 1
            print(f"[IGNORADO] {arquivo.name}")
            continue

        total_analisados += 1

        # Verificacao da retencao
        if data_backup < data_limite:

            total_antigos += 1

            if MODO_SIMULACAO:

                print(
                    f"[SIMULACAO] Excluiria: {arquivo.name}"
                )

            else:

                arquivo.unlink()

                total_excluidos += 1

                print(f"[EXCLUIDO] {arquivo.name}")

        else:

            total_preservados += 1

            print(f"[MANTIDO] {arquivo.name}")

    # Resumo da operacao
    print("\n===== RESUMO DA LIMPEZA =====\n")

    print(f"Ambiente: {ambiente}")
    print(f"Backups analisados: {total_analisados}")
    print(f"Backups antigos: {total_antigos}")
    print(f"Backups excluidos: {total_excluidos}")
    print(f"Backups dentro do prazo: {total_preservados}")
    print(f"Itens ignorados: {total_ignorados}")

    print("\nLimpeza finalizada com sucesso!")

    print("=" * 45)

except Exception as erro:

    print(f"Erro na limpeza de backups: {erro}")

    raise SystemExit(1)
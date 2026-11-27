import os
import subprocess
import sys
import logging
import time
from pathlib import Path


# ==========================================
# CONFIGURACOES DO AMBIENTE
# ==========================================

DATABASE = os.getenv(
    "DB_NAME", "empresa_automacao_demo"
)

BANCOS_PERMITIDOS = (
    "empresa_automacao",
    "empresa_automacao_demo"
)

if DATABASE not in BANCOS_PERMITIDOS:
    sys.exit("Banco de dados nao autorizado.")

AMBIENTE_DEMO = DATABASE == "empresa_automacao_demo"

AMBIENTE = (
    "DEMONSTRACAO"
    if AMBIENTE_DEMO
    else "OPERACIONAL"
)

if not AMBIENTE_DEMO:
    if os.getenv("PERMITIR_ENVIO_REAL") != "1":
        sys.exit(
            "Execucao operacional bloqueada por seguranca."
        )


# ==========================================
# DIRETORIOS
# ==========================================

pasta = Path(__file__).resolve().parent

pasta_logs = pasta / "logs"
pasta_logs.mkdir(exist_ok=True)

arquivo_log = (
    "robo_financeiro_demo.log"
    if AMBIENTE_DEMO
    else "robo_financeiro.log"
)


# ==========================================
# CONFIGURACAO DOS LOGS
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    handlers=[
        logging.FileHandler(
            pasta_logs / arquivo_log,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)


# ==========================================
# VARIAVEIS COMPARTILHADAS
# ==========================================

ambiente_execucao = os.environ.copy()

ambiente_execucao["DB_NAME"] = DATABASE


# ==========================================
# ROTINAS DO ROBO
# ==========================================

rotinas = [
    ("Exportacao financeira", "exportar_excel.py"),
    ("Geracao do dashboard", "dashboard_v3.py"),
    ("Backup do relatorio", "backup_relatorio.py"),
    ("Limpeza de backups", "limpar_backups.py"),
    ("Envio do e-mail", "enviar_email.py")
]


# ==========================================
# INICIO DA EXECUCAO
# ==========================================

inicio = time.perf_counter()

rotinas_concluidas = 0

logging.info("=" * 60)
logging.info("INICIANDO ROBO FINANCEIRO")
logging.info(f"Ambiente: {AMBIENTE}")
logging.info(f"Banco de dados: {DATABASE}")
logging.info(f"Total de rotinas: {len(rotinas)}")
logging.info("=" * 60)

try:

    # Validacao dos arquivos

    for nome, arquivo in rotinas:

        if not (pasta / arquivo).is_file():

            raise FileNotFoundError(
                f"Script nao encontrado: {arquivo}"
            )

    # Execucao sequencial

    for numero, (nome, arquivo) in enumerate(
        rotinas, start=1
    ):

        inicio_rotina = time.perf_counter()

        logging.info(
            f"[{numero}/{len(rotinas)}] Executando: {nome}"
        )

        subprocess.run(
            [
                sys.executable,
                str(pasta / arquivo)
            ],
            cwd=pasta,
            env=ambiente_execucao,
            check=True
        )

        duracao_rotina = (
            time.perf_counter() - inicio_rotina
        )

        rotinas_concluidas += 1

        logging.info(
            f"Concluido: {nome} | "
            f"{duracao_rotina:.2f} segundos"
        )

    logging.info("=" * 60)
    logging.info("TODAS AS ROTINAS FINALIZADAS")
    logging.info("STATUS FINAL: SUCESSO")

except subprocess.CalledProcessError as erro:

    logging.exception(
        f"Falha na rotina: {nome}"
    )

    logging.error(
        f"Codigo de erro: {erro.returncode}"
    )

    logging.error("STATUS FINAL: FALHA")

    sys.exit(1)

except Exception as erro:

    logging.exception(
        f"Erro inesperado: {erro}"
    )

    logging.error("STATUS FINAL: FALHA")

    sys.exit(1)

finally:

    duracao = time.perf_counter() - inicio

    logging.info(
        f"Rotinas concluidas: "
        f"{rotinas_concluidas}/{len(rotinas)}"
    )

    logging.info(
        f"Tempo total de execucao: "
        f"{duracao:.2f} segundos"
    )

    logging.info("=" * 60)
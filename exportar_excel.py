
import os
import mysql.connector
import pandas as pd
import keyring

from pathlib import Path
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# Configuracoes do banco de dados

HOST = os.getenv("DB_HOST", "localhost")
PORT = int(os.getenv("DB_PORT", "3306"))
USER = os.getenv("DB_USER", "root")
DATABASE = os.getenv("DB_NAME", "empresa_automacao_demo")

BASE_DIR = Path(__file__).resolve().parent

try:
    senha = keyring.get_password("robo_financeiro", USER)

    if senha is None:
        raise RuntimeError(
            "Senha do MySQL nao encontrada. "
            "Execute configurar_senha.py."
        )

    conexao = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=senha,
        database=DATABASE
    )

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            c.id_conta,
            f.razao_social AS fornecedor,
            c.descricao,
            c.valor,
            c.vencimento,
            c.data_pagamento,
            c.status,
            CASE
                WHEN c.status <> 'PAGO'
                THEN GREATEST(
                    DATEDIFF(CURDATE(), c.vencimento), 0
                )
                ELSE 0
            END AS dias_atraso
        FROM contas_pagar AS c
        INNER JOIN fornecedores AS f
            ON c.id_fornecedor = f.id_fornecedor
        ORDER BY c.vencimento ASC
    """)

    dados = cursor.fetchall()
    colunas = [coluna[0] for coluna in cursor.description]

    df = pd.DataFrame(dados, columns=colunas)
    df["valor"] = df["valor"].astype(float)

    cursor.close()
    conexao.close()

    # Indicadores financeiros

    total_despesas = df["valor"].sum()

    total_vencido = df.loc[
        df["status"] == "VENCIDO", "valor"
    ].sum()

    total_pendente = df.loc[
        df["status"] == "PENDENTE", "valor"
    ].sum()

    total_pago = df.loc[
        df["status"] == "PAGO", "valor"
    ].sum()

    total_aberto = total_vencido + total_pendente

    percentual_atraso = (
        total_vencido / total_despesas
        if total_despesas > 0 else 0
    )

    # Criacao do resumo financeiro

    resumo = pd.DataFrame({
        "Indicador": [
            "Total de contas",
            "Total de despesas",
            "Total vencido",
            "Total pendente",
            "Total pago",
            "Percentual em atraso",
            "Total em aberto"
        ],
        "Resultado": [
            len(df),
            total_despesas,
            total_vencido,
            total_pendente,
            total_pago,
            percentual_atraso,
            total_aberto
        ]
    })

    # Separacao das contas vencidas

    vencidas = df[df["status"] == "VENCIDO"].copy()

    # Separacao dos relatorios

    if DATABASE == "empresa_automacao":
        nome_arquivo = "relatorio_financeiro.xlsx"
    else:
        nome_arquivo = "relatorio_financeiro_demo.xlsx"

    arquivo = BASE_DIR / nome_arquivo

    # Exportacao para Excel

    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:

        resumo.to_excel(
            writer,
            sheet_name="Resumo Financeiro",
            index=False
        )

        df.to_excel(
            writer,
            sheet_name="Contas a Pagar",
            index=False
        )

        vencidas.to_excel(
            writer,
            sheet_name="Contas Vencidas",
            index=False
        )

        # Formatacao das planilhas

        for planilha in writer.book.worksheets:

            planilha.freeze_panes = "A2"
            planilha.sheet_view.showGridLines = False

            for celula in planilha[1]:
                celula.fill = PatternFill(
                    "solid", fgColor="17365D"
                )
                celula.font = Font(
                    color="FFFFFF", bold=True
                )
                celula.alignment = Alignment(
                    horizontal="center"
                )

            for coluna in planilha.columns:
                largura = max(
                    len(str(celula.value or ""))
                    for celula in coluna
                )

                letra = get_column_letter(coluna[0].column)

                planilha.column_dimensions[letra].width = (
                    largura + 5
                )

            if planilha.title != "Resumo Financeiro":

                planilha.auto_filter.ref = planilha.dimensions

                for linha in range(2, planilha.max_row + 1):

                    planilha[f"D{linha}"].number_format = (
                        '"R$" #,##0.00'
                    )

                    planilha[f"E{linha}"].number_format = "dd/mm/yyyy"
                    planilha[f"F{linha}"].number_format = "dd/mm/yyyy"

                    status = planilha[f"G{linha}"]

                    cores = {
                        "VENCIDO": "FFC7CE",
                        "PENDENTE": "FFEB9C",
                        "PAGO": "C6EFCE"
                    }

                    if status.value in cores:
                        status.fill = PatternFill(
                            "solid",
                            fgColor=cores[status.value]
                        )

        # Formatacao do resumo

        aba_resumo = writer.book["Resumo Financeiro"]

        aba_resumo["B2"].number_format = "0"

        for linha in range(3, 7):
            aba_resumo[f"B{linha}"].number_format = (
                '"R$" #,##0.00'
            )

        aba_resumo["B7"].number_format = "0.00%"
        aba_resumo["B8"].number_format = '"R$" #,##0.00'

    print("\n===== EXPORTACAO FINANCEIRA =====\n")
    print(f"Banco de dados: {DATABASE}")
    print(f"Total de contas exportadas: {len(df)}")
    print(f"Contas vencidas: {len(vencidas)}")
    print(f"Total de despesas: R$ {total_despesas:.2f}")
    print(f"Total em aberto: R$ {total_aberto:.2f}")
    print(f"Arquivo salvo em: {arquivo}")
    print("\nRelatorio Excel gerado com sucesso!")

except Exception as erro:
    print(f"Erro: {erro}")
    raise SystemExit(1)

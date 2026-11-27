import os

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import DataBarRule
from openpyxl.utils import get_column_letter


# ==========================================
# CONFIGURACOES DO AMBIENTE
# ==========================================

DATABASE = os.getenv(
    "DB_NAME", "empresa_automacao_demo"
)

if DATABASE not in (
    "empresa_automacao",
    "empresa_automacao_demo"
):
    raise SystemExit("Banco de dados nao autorizado.")

AMBIENTE_DEMO = DATABASE == "empresa_automacao_demo"

AMBIENTE = (
    "DEMONSTRACAO"
    if AMBIENTE_DEMO
    else "OPERACIONAL"
)

pasta = Path(__file__).resolve().parent

arquivo = pasta / (
    "relatorio_financeiro_demo.xlsx"
    if AMBIENTE_DEMO
    else "relatorio_financeiro.xlsx"
)

if not arquivo.is_file():
    raise SystemExit(
        f"Relatorio nao encontrado: {arquivo.name}"
    )


# ==========================================
# CARREGAMENTO DO RELATORIO
# ==========================================

wb = load_workbook(arquivo)

contas = wb["Contas a Pagar"]

linhas = [
    r for r in contas.iter_rows(
        min_row=2,
        values_only=True
    )
    if r[0] is not None
]

if "Dashboard" in wb.sheetnames:
    del wb["Dashboard"]

ws = wb.create_sheet("Dashboard", 0)


# ==========================================
# IDENTIDADE VISUAL
# ==========================================

BG = "EEF2F7"
WHITE = "FFFFFF"
NAVY = "142D4E"
MUTED = "64748B"

RED = "BE3450"
GOLD = "A66A12"
GREEN = "087D68"
BLUE = "4268D6"

moeda = '"R$" #,##0.00'

ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 85
ws.sheet_properties.tabColor = BLUE

for c in range(1, 25):
    ws.column_dimensions[
        get_column_letter(c)
    ].width = 5.5

for r in range(1, 39):

    ws.row_dimensions[r].height = 19

    for c in range(1, 25):

        ws.cell(r, c).fill = PatternFill(
            "solid",
            fgColor=BG
        )


# ==========================================
# FUNCAO DE FORMATACAO
# ==========================================

def bloco(
    r, c, r2, c2,
    valor="",
    cor=NAVY,
    tam=11,
    fundo=WHITE,
    bold=False,
    fmt=None,
    align="left"
):

    if (r, c) != (r2, c2):

        ws.merge_cells(
            start_row=r,
            start_column=c,
            end_row=r2,
            end_column=c2
        )

    for row in ws.iter_rows(
        min_row=r,
        max_row=r2,
        min_col=c,
        max_col=c2
    ):

        for cell in row:

            cell.fill = PatternFill(
                "solid",
                fgColor=fundo
            )

    cell = ws.cell(r, c)

    cell.value = valor

    cell.font = Font(
        name="Calibri",
        size=tam,
        color=cor,
        bold=bold
    )

    cell.alignment = Alignment(
        horizontal=align,
        vertical="center",
        indent=1 if align == "left" else 0,
        shrink_to_fit=True
    )

    if fmt:
        cell.number_format = fmt

    return cell


# ==========================================
# INDICADORES FINANCEIROS
# ==========================================

somas = defaultdict(float)
ranking = defaultdict(float)
atrasadas = []

for l in linhas:

    valor = float(l[3] or 0)

    status = str(l[6]).upper().strip()

    somas[status] += valor

    ranking[str(l[1])] += valor

    if status == "VENCIDO":
        atrasadas.append(l)

total = sum(somas.values())

vencido = somas["VENCIDO"]
pendente = somas["PENDENTE"]
pago = somas["PAGO"]

total_aberto = vencido + pendente

percentual_atraso = (
    vencido / total
    if total else 0
)


# ==========================================
# CABECALHO
# ==========================================

bloco(
    2, 2, 2, 23,
    f"FINANCE / CONTROL CENTER | {AMBIENTE}",
    "B9CDF4", 10, NAVY, True
)

bloco(
    3, 2, 4, 23,
    "Visão financeira",
    WHITE, 26, NAVY, True
)

bloco(
    5, 2, 5, 23,
    "Contas a pagar | Atualizado em "
    + datetime.now().strftime("%d/%m/%Y %H:%M"),
    WHITE, 11, NAVY
)


# ==========================================
# CARDS FINANCEIROS
# ==========================================

indicadores = [
    (2, "Despesas totais", total, NAVY),
    (8, "Vencido", vencido, RED),
    (14, "Pendente", pendente, GOLD),
    (20, "Pago", pago, GREEN)
]

for c, t, v, cor in indicadores:

    fim = min(c + 4, 23)

    bloco(
        7, c, 7, fim,
        t, MUTED, 11,
        bold=True
    )

    bloco(
        8, c, 9, fim,
        v, cor, 19,
        bold=True,
        fmt=moeda
    )

    bloco(
        10, c, 10, fim,
        "Valor acumulado",
        MUTED, 9
    )


# ==========================================
# DISTRIBUICAO FINANCEIRA
# ==========================================

bloco(
    12, 2, 12, 11,
    "Distribuição financeira",
    NAVY, 15,
    bold=True
)

bloco(
    13, 2, 13, 11,
    f"{len(linhas)} contas | "
    f"{len(atrasadas)} vencidas",
    MUTED, 10
)

distribuicao = [
    ("Vencido", vencido, RED),
    ("Pendente", pendente, GOLD),
    ("Pago", pago, GREEN)
]

for r, (nome, v, cor) in zip(
    [15, 18, 21],
    distribuicao
):

    bloco(
        r, 2, r, 6,
        nome, cor, 11,
        bold=True
    )

    bloco(
        r, 7, r, 11,
        v, cor, 11,
        fmt=moeda,
        align="right"
    )

    bloco(
        r + 1, 2, r + 1, 11,
        v / total if total else 0,
        cor, 11,
        fmt="0.0%",
        align="right"
    )

    ws.conditional_formatting.add(
        f"B{r + 1}",
        DataBarRule(
            start_type="num",
            start_value=0,
            end_type="num",
            end_value=1,
            color=cor,
            showValue=True
        )
    )


# ==========================================
# RANKING DE FORNECEDORES
# ==========================================

bloco(
    12, 13, 12, 23,
    "Ranking de fornecedores",
    NAVY, 15,
    bold=True
)

bloco(
    13, 13, 13, 23,
    "Top 5 por valor de despesas",
    MUTED, 10
)

top_fornecedores = sorted(
    ranking.items(),
    key=lambda x: -x[1]
)[:5]

for r, (nome, v) in enumerate(
    top_fornecedores, 15
):

    bloco(
        r, 13, r, 18,
        nome, NAVY, 11
    )

    bloco(
        r, 19, r, 23,
        v, NAVY, 11,
        fmt=moeda,
        align="right"
    )

    ws.conditional_formatting.add(
        f"S{r}",
        DataBarRule(
            start_type="num",
            start_value=0,
            end_type="num",
            end_value=max(ranking.values()) or 1,
            color="B9CDF4",
            showValue=True
        )
    )


# ==========================================
# INDICE DE ATRASO
# ==========================================

bloco(
    22, 13, 22, 23,
    "Índice financeiro de atraso",
    MUTED, 11
)

bloco(
    23, 13, 24, 23,
    percentual_atraso,
    RED, 23,
    bold=True,
    fmt="0.00%"
)


# ==========================================
# CONTAS VENCIDAS
# ==========================================

bloco(
    26, 2, 27, 23,
    "Contas vencidas / Prioridades",
    NAVY, 16,
    bold=True
)

cabecalhos = [
    (2, 10, "Descrição"),
    (11, 16, "Fornecedor"),
    (17, 20, "Valor"),
    (21, 23, "Dias em atraso")
]

for c, e, t in cabecalhos:

    bloco(
        28, c, 28, e,
        t, MUTED, 10,
        "E2E8F0", True
    )

prioridades = sorted(
    atrasadas,
    key=lambda x: float(x[7] or 0),
    reverse=True
)[:8]

for r, l in enumerate(prioridades, 29):

    f = WHITE if r % 2 else "F8FAFC"

    bloco(
        r, 2, r, 10,
        l[2], fundo=f
    )

    bloco(
        r, 11, r, 16,
        l[1], fundo=f
    )

    bloco(
        r, 17, r, 20,
        l[3],
        fundo=f,
        fmt=moeda,
        align="right"
    )

    bloco(
        r, 21, r, 23,
        l[7], RED,
        fundo=f,
        bold=True,
        align="center"
    )

if not atrasadas:

    bloco(
        29, 2, 29, 23,
        "Nenhuma conta vencida",
        GREEN
    )


# ==========================================
# RODAPE
# ==========================================

rodape = (
    "MYSQL + PYTHON | Dados fictícios"
    if AMBIENTE_DEMO
    else "MYSQL + PYTHON | Relatório gerencial interno"
)

bloco(
    38, 2, 38, 23,
    rodape,
    MUTED, 9, BG
)


# ==========================================
# CONFIGURACAO DE IMPRESSAO
# ==========================================

ws.print_options.horizontalCentered = True

ws.print_area = "A1:X38"

ws.sheet_properties.pageSetUpPr.fitToPage = True

ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 1

wb.active = 0


# ==========================================
# SALVAMENTO
# ==========================================

try:

    wb.save(arquivo)

except PermissionError:

    raise SystemExit(
        "Feche o Excel e execute novamente."
    )

finally:

    wb.close()


# ==========================================
# RESULTADO DA EXECUCAO
# ==========================================

print("\n===== DASHBOARD FINANCEIRO V3 =====\n")

print(f"Banco de dados: {DATABASE}")
print(f"Ambiente: {AMBIENTE}")
print(f"Total de contas: {len(linhas)}")
print(f"Contas vencidas: {len(atrasadas)}")
print(f"Total de despesas: R$ {total:.2f}")
print(f"Total em aberto: R$ {total_aberto:.2f}")
print(f"Percentual em atraso: {percentual_atraso:.2%}")
print(f"Arquivo: {arquivo.name}")

print("\nDashboard V3 criado com sucesso!")
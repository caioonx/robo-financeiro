from pathlib import Path
from datetime import datetime
from collections import defaultdict
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import DoughnutChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.utils import get_column_letter

arquivo = Path(__file__).parent / 'relatorio_financeiro.xlsx'
wb = load_workbook(arquivo)
if 'Dashboard' in wb.sheetnames:
    del wb['Dashboard']
ws = wb.create_sheet('Dashboard', 0)
resumo = wb['Resumo Financeiro']
contas = wb['Contas a Pagar']
qtd, total, vencido, pendente, pago, atraso = [resumo.cell(i, 2).value or 0 for i in range(2, 8)]
BG, PANEL, WHITE, MUTED = '0D1424', '192338', 'FFFFFF', 'B0BED2'
PURPLE, RED, GOLD, GREEN = 'A78BFA', 'FB7185', 'FBBF24', '34D399'
moeda = '"R$" #,##0.00'
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 75
ws.sheet_properties.tabColor = PURPLE
for c in range(1, 17):
    ws.column_dimensions[get_column_letter(c)].width = 10
for r in range(1, 48):
    ws.row_dimensions[r].height = 20
    for c in range(1, 17):
        ws.cell(r,c).fill = PatternFill('solid', fgColor=BG)

def bloco(area, valor, cor=WHITE, tamanho=12, fundo=PANEL, bold=False, alinhamento='left', formato=None):
    ws.merge_cells(area)
    for row in ws[area]:
        for cell in row:
            cell.fill = PatternFill('solid', fgColor=fundo)
    cell = ws[area.split(':')[0]]
    cell.value = valor
    cell.font = Font(name='Calibri', size=tamanho, color=cor, bold=bold)
    cell.alignment = Alignment(horizontal=alinhamento, vertical='center', indent=1 if alinhamento=='left' else 0)
    if formato:
        cell.number_format = formato

bloco('B2:O2','FINANCE  /  ANALYTICS',PURPLE,11,BG,True)
bloco('B3:O4','Visão financeira',WHITE,28,BG,True)
bloco('B5:O5','Contas a pagar  |  Gerado em '+datetime.now().strftime('%d/%m/%Y %H:%M'),MUTED,11,BG)
for titulo, valor, cor, a,b, fmt in [
 ('Despesas totais',total,PURPLE,'B7:G7','B8:G9',moeda),
 ('Contas vencidas',vencido,RED,'I7:O7','I8:O9',moeda),
 ('Valor pendente',pendente,GOLD,'B11:G11','B12:G13',moeda),
 ('Total pago',pago,GREEN,'I11:O11','I12:O13',moeda),
 ('Contas cadastradas',qtd,WHITE,'B15:G15','B16:G17','00'),
 ('Índice de atraso',atraso,RED,'I15:O15','I16:O17','0.00%')]:
    bloco(a,titulo,MUTED,12)
    bloco(b,valor,cor,24,bold=True,formato=fmt)

bloco('B19:G19','Distribuição das despesas',WHITE,14,bold=True)
bloco('I19:O19','Despesas por fornecedor',WHITE,14,bold=True)
for r in range(20,32):
    for c in list(range(2,8))+list(range(9,16)):
        ws.cell(r,c).fill=PatternFill('solid',fgColor=PANEL)
for r,(nome,valor) in enumerate([('Vencido',vencido),('Pendente',pendente),('Pago',pago)],2):
    ws.cell(r,18,nome); ws.cell(r,19,valor)
chart=DoughnutChart(); chart.holeSize=72; chart.legend=None
chart.add_data(Reference(ws,min_col=19,min_row=2,max_row=4))
chart.set_categories(Reference(ws,min_col=18,min_row=2,max_row=4))
for i,cor in enumerate([RED,GOLD,GREEN]):
    p=DataPoint(idx=i); p.graphicalProperties.solidFill=cor; p.graphicalProperties.line.noFill=True
    chart.series[0].data_points.append(p)
from openpyxl.chart.shapes import GraphicalProperties
chart.graphical_properties=GraphicalProperties(solidFill=PANEL)
chart.graphical_properties.line.noFill=True
chart.visible_cells_only=False
chart.width=10.5; chart.height=5.5
ws.add_chart(chart,'B20')
for r,(nome,valor,cor) in enumerate([('Vencido',vencido,RED),('Pendente',pendente,GOLD),('Pago',pago,GREEN)],29):
    bloco(f'B{r}:D{r}',nome,cor,11)
    bloco(f'E{r}:G{r}',valor,cor,11,formato=moeda)
ranking=defaultdict(float); atrasadas=[]
for linha in contas.iter_rows(min_row=2,values_only=True):
    if len(linha)<8 or not linha[1]: continue
    ranking[linha[1]]+=float(linha[3] or 0)
    if linha[6]=='VENCIDO': atrasadas.append(linha)
ranking=sorted(ranking.items(),key=lambda x:x[1],reverse=True)[:5]
maximo=max((v for _,v in ranking),default=1) or 1
for i,(nome,valor) in enumerate(ranking):
    r=21+i*2
    bloco(f'I{r}:L{r}',nome,MUTED,11)
    bloco(f'M{r}:O{r}',valor,WHITE,11,formato=moeda,alinhamento='right')
    for c in range(9,16):
        ws.cell(r+1,c).fill=PatternFill('solid',fgColor=PURPLE if c-9 < round(7*valor/maximo) else '29354B')
bloco('B33:O34','Contas que precisam de atenção',WHITE,16,bold=True)
bloco('B35:H35','Despesa',MUTED,11,bold=True)
bloco('I35:L35','Valor',MUTED,11,bold=True)
bloco('M35:O35','Dias em atraso',MUTED,11,bold=True)
for r,linha in enumerate(sorted(atrasadas,key=lambda x:x[7] or 0,reverse=True)[:8],36):
    fundo=PANEL if r%2==0 else '202D43'
    bloco(f'B{r}:H{r}',linha[2],WHITE,11,fundo)
    bloco(f'I{r}:L{r}',linha[3],WHITE,11,fundo,formato=moeda)
    bloco(f'M{r}:O{r}',linha[7],RED,11,fundo,True)
if not atrasadas: bloco('B36:O36','Nenhuma conta vencida',GREEN,12)
bloco('B45:O45','MYSQL + PYTHON  /  FINANCIAL AUTOMATION',MUTED,10,BG,alinhamento='center')
ws.column_dimensions['R'].hidden=True
ws.column_dimensions['S'].hidden=True
ws.print_area='A1:P46'
wb.active=0
wb.save(arquivo)
print('Dashboard atualizado com sucesso!')
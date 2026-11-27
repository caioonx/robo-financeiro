import os
import smtplib
import ssl
import keyring

from email.message import EmailMessage
from pathlib import Path
from datetime import datetime
from openpyxl import load_workbook


# ==========================================
# CONFIGURACOES DO AMBIENTE
# ==========================================

DATABASE = os.getenv(
    "DB_NAME", "empresa_automacao_demo"
)

AMBIENTE_DEMO = DATABASE == "empresa_automacao_demo"

PASTA = Path(__file__).resolve().parent


def moeda(valor):
    return (
        f"R$ {float(valor):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


try:

    # ==========================================
    # CREDENCIAIS E SEGURANCA
    # ==========================================

    if DATABASE not in (
        "empresa_automacao",
        "empresa_automacao_demo"
    ):
        raise ValueError("Banco de dados nao autorizado.")

    email = os.getenv("EMAIL_REMETENTE") or keyring.get_password(
        "robo_financeiro_email", "email"
    )

    senha = keyring.get_password(
        "robo_financeiro_email", "senha"
    )

    if not email or not senha:
        raise ValueError(
            "Credenciais de e-mail nao encontradas."
        )

    if AMBIENTE_DEMO:

        destinatario = email

        arquivo = PASTA / "relatorio_financeiro_demo.xlsx"

        ambiente = "DEMONSTRACAO"

        aviso = (
            "Relatorio demonstrativo elaborado "
            "exclusivamente com dados ficticios."
        )

    else:

        if os.getenv("PERMITIR_ENVIO_REAL") != "1":
            raise RuntimeError(
                "Envio de dados reais bloqueado por seguranca."
            )

        destinatario = os.getenv(
            "EMAIL_DESTINATARIO", email
        )

        arquivo = PASTA / "relatorio_financeiro.xlsx"

        ambiente = "OPERACIONAL"

        aviso = "Relatorio financeiro de uso interno."

    if not arquivo.exists():
        raise FileNotFoundError(
            f"Relatorio nao encontrado: {arquivo.name}"
        )

    # ==========================================
    # LEITURA DOS INDICADORES
    # ==========================================

    wb = load_workbook(
        arquivo,
        data_only=True,
        read_only=True
    )

    try:

        resumo = wb["Resumo Financeiro"]

        total_contas = resumo["B2"].value
        total_despesas = resumo["B3"].value
        total_vencido = resumo["B4"].value
        total_pendente = resumo["B5"].value
        total_pago = resumo["B6"].value
        percentual_atraso = resumo["B7"].value

        total_aberto = total_vencido + total_pendente

    finally:

        wb.close()

    data = datetime.now().strftime("%d/%m/%Y")
    horario = datetime.now().strftime("%H:%M")

    percentual = (
        f"{percentual_atraso:.2%}"
        .replace(".", ",")
    )

    # ==========================================
    # CONFIGURACAO DA MENSAGEM
    # ==========================================

    mensagem = EmailMessage()

    mensagem["Subject"] = (
        f"[{ambiente}] Relatorio Financeiro | {data}"
    )

    mensagem["From"] = email
    mensagem["To"] = destinatario

    mensagem.set_content(
        f"Segue o relatorio financeiro em anexo.\n\n"
        f"Ambiente: {ambiente}\n"
        f"{aviso}"
    )

    # ==========================================
    # DASHBOARD HTML
    # ==========================================

    html = f"""
    <html>
    <body style="font-family:Arial;
                 background-color:#eef2f7;
                 padding:25px;">

        <div style="max-width:650px;
                    margin:auto;
                    background-color:white;
                    border-radius:12px;
                    overflow:hidden;">

            <div style="background:#142b49;
                        color:white;
                        padding:30px;">

                <small>FINANCE / CONTROL CENTER</small>

                <h1>Relatorio Financeiro</h1>

                <p>Atualizado em {data} as {horario}</p>

                <p>Ambiente: {ambiente}</p>

            </div>

            <div style="padding:25px;">

                <div style="background:#e0f2fe;
                            color:#075985;
                            padding:15px;
                            border-radius:8px;">

                    <b>{aviso}</b>

                </div>

                <p>Prezados,</p>

                <p>Segue o resumo financeiro atualizado,
                gerado automaticamente pelo sistema.</p>

                <table style="width:100%;
                              border-spacing:10px;">

                    <tr>

                        <td style="background:#f1f5f9;
                                   padding:20px;">

                            Total de despesas

                            <h2 style="color:#142b49;">
                                {moeda(total_despesas)}
                            </h2>

                        </td>

                        <td style="background:#fff1f2;
                                   padding:20px;">

                            Total vencido

                            <h2 style="color:#dc3545;">
                                {moeda(total_vencido)}
                            </h2>

                        </td>

                    </tr>

                    <tr>

                        <td style="background:#fffbeb;
                                   padding:20px;">

                            Total pendente

                            <h2 style="color:#b7791f;">
                                {moeda(total_pendente)}
                            </h2>

                        </td>

                        <td style="background:#ecfdf5;
                                   padding:20px;">

                            Total pago

                            <h2 style="color:#16835d;">
                                {moeda(total_pago)}
                            </h2>

                        </td>

                    </tr>

                    <tr>

                        <td style="background:#eff6ff;
                                   padding:20px;">

                            Total em aberto

                            <h2 style="color:#2563eb;">
                                {moeda(total_aberto)}
                            </h2>

                        </td>

                        <td style="background:#f1f5f9;
                                   padding:20px;">

                            Total de contas

                            <h2 style="color:#142b49;">
                                {total_contas}
                            </h2>

                        </td>

                    </tr>

                </table>

                <p>
                    <b>Percentual financeiro em atraso:</b>

                    <span style="color:#dc3545;">
                        {percentual}
                    </span>
                </p>

                <hr>

                <p>O relatorio financeiro completo
                encontra-se em anexo.</p>

                <p>Atenciosamente,<br>
                <b>Robo Financeiro</b></p>

            </div>

            <div style="background:#142b49;
                        color:white;
                        text-align:center;
                        padding:15px;
                        font-size:12px;">

                Mensagem gerada automaticamente
                pelo sistema de automacao financeira.

            </div>

        </div>

    </body>
    </html>
    """

    mensagem.add_alternative(
        html,
        subtype="html"
    )

    # ==========================================
    # ANEXO DO RELATORIO
    # ==========================================

    with open(arquivo, "rb") as anexo:

        mensagem.add_attachment(
            anexo.read(),
            maintype="application",
            subtype=(
                "vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
            filename=arquivo.name
        )

    # ==========================================
    # ENVIO SEGURO VIA GMAIL
    # ==========================================

    contexto = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        context=contexto,
        timeout=30
    ) as servidor:

        servidor.login(email, senha)

        servidor.send_message(mensagem)

    # ==========================================
    # RESULTADO DA EXECUCAO
    # ==========================================

    print("\n===== ENVIO DE E-MAIL =====\n")

    print(f"Banco de dados: {DATABASE}")
    print(f"Ambiente: {ambiente}")
    print(f"Destinatario: {destinatario}")
    print(f"Anexo: {arquivo.name}")
    print(f"Total de contas: {total_contas}")
    print(f"Total de despesas: {moeda(total_despesas)}")
    print(f"Total em aberto: {moeda(total_aberto)}")

    print("\nE-mail enviado com sucesso!")

except Exception as erro:

    print(f"Erro no envio do e-mail: {erro}")

    raise SystemExit(1)
import keyring
from getpass import getpass

print("===== CONFIGURACAO DE E-MAIL =====")

email = input("Digite seu Gmail: ").strip()

senha = getpass("Digite a senha de aplicativo: ")
senha = senha.replace(" ", "")

if not email or len(senha) != 16:
    raise ValueError("E-mail ou senha de aplicativo invalida.")

keyring.set_password(
    "robo_financeiro_email",
    "email",
    email
)

keyring.set_password(
    "robo_financeiro_email",
    "senha",
    senha
)

print("\nCredenciais armazenadas com sucesso!")

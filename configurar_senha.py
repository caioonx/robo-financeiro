import keyring
from getpass import getpass

senha = getpass("Digite a senha do MySQL: ")

keyring.set_password(
    "robo_financeiro",
    "root",
    senha
)

print("Senha armazenada com sucesso!")